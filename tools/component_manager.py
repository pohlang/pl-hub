"""
PLHub Component Library System
Manages reusable components with versioning, dependencies, and marketplace integration

Features:
- Component registry with metadata
- Semantic versioning (MAJOR.MINOR.PATCH)
- Dependency resolution
- Component templates
- Import/export functionality
- Marketplace integration
- License management
- Update notifications
"""

import json
import shutil
import hashlib
import requests
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import semver


class ComponentType(Enum):
    """Types of components"""
    WIDGET = "widget"
    LAYOUT = "layout"
    STYLE = "style"
    UTILITY = "utility"
    PLUGIN = "plugin"
    THEME = "theme"


class ComponentStatus(Enum):
    """Component status"""
    INSTALLED = "installed"
    AVAILABLE = "available"
    OUTDATED = "outdated"
    DEPRECATED = "deprecated"


@dataclass
class ComponentDependency:
    """Component dependency specification"""
    name: str
    version_constraint: str  # e.g., "^1.0.0", ">=2.0.0", "~1.5.0"
    optional: bool = False
    
    def is_satisfied_by(self, version: str) -> bool:
        """Check if version satisfies constraint"""
        try:
            return semver.match(version, self.version_constraint)
        except:
            return False


@dataclass
class ComponentMetadata:
    """Component metadata and configuration"""
    name: str
    version: str
    type: ComponentType
    author: str
    description: str
    license: str = "MIT"
    keywords: List[str] = field(default_factory=list)
    dependencies: List[ComponentDependency] = field(default_factory=list)
    repository: Optional[str] = None
    homepage: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    downloads: int = 0
    rating: float = 0.0
    status: ComponentStatus = ComponentStatus.AVAILABLE
    
    # Component files
    files: List[str] = field(default_factory=list)
    entry_point: Optional[str] = None
    
    # Platform compatibility
    platforms: List[str] = field(default_factory=lambda: ["all"])
    
    # Minimum requirements
    min_plhub_version: Optional[str] = None
    min_pohlang_version: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data['type'] = self.type.value
        data['status'] = self.status.value
        data['dependencies'] = [
            {
                'name': dep.name,
                'version_constraint': dep.version_constraint,
                'optional': dep.optional
            }
            for dep in self.dependencies
        ]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ComponentMetadata':
        """Create from dictionary"""
        data['type'] = ComponentType(data['type'])
        data['status'] = ComponentStatus(data.get('status', 'available'))
        data['dependencies'] = [
            ComponentDependency(**dep)
            for dep in data.get('dependencies', [])
        ]
        return cls(**data)
    
    def get_id(self) -> str:
        """Get unique component ID"""
        return f"{self.name}@{self.version}"
    
    def checksum(self, component_dir: Path) -> str:
        """Calculate checksum of component files"""
        hasher = hashlib.sha256()
        for file_rel in self.files:
            file_path = component_dir / file_rel
            if file_path.exists():
                hasher.update(file_path.read_bytes())
        return hasher.hexdigest()


class ComponentRegistry:
    """Local component registry"""
    
    def __init__(self, registry_dir: Path):
        self.registry_dir = registry_dir
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        
        self.components_dir = self.registry_dir / "components"
        self.components_dir.mkdir(exist_ok=True)
        
        self.index_file = self.registry_dir / "index.json"
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, ComponentMetadata]:
        """Load component index"""
        if self.index_file.exists():
            try:
                data = json.loads(self.index_file.read_text())
                return {
                    name: ComponentMetadata.from_dict(meta)
                    for name, meta in data.items()
                }
            except:
                return {}
        return {}
    
    def _save_index(self):
        """Save component index"""
        data = {
            name: meta.to_dict()
            for name, meta in self.index.items()
        }
        self.index_file.write_text(json.dumps(data, indent=2))
    
    def register(self, metadata: ComponentMetadata, component_dir: Path) -> bool:
        """Register a new component"""
        try:
            component_id = metadata.get_id()
            
            # Check if already registered
            if component_id in self.index:
                print(f"Component {component_id} already registered")
                return False
            
            # Copy component files to registry
            dest_dir = self.components_dir / metadata.name / metadata.version
            dest_dir.mkdir(parents=True, exist_ok=True)
            
            for file_rel in metadata.files:
                src_file = component_dir / file_rel
                dest_file = dest_dir / file_rel
                dest_file.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src_file, dest_file)
            
            # Save metadata
            metadata_file = dest_dir / "component.json"
            metadata_file.write_text(json.dumps(metadata.to_dict(), indent=2))
            
            # Update index
            metadata.status = ComponentStatus.INSTALLED
            self.index[component_id] = metadata
            self._save_index()
            
            print(f"✓ Registered component: {component_id}")
            return True
            
        except Exception as e:
            print(f"Failed to register component: {e}")
            return False
    
    def unregister(self, name: str, version: Optional[str] = None) -> bool:
        """Unregister a component"""
        try:
            if version:
                component_id = f"{name}@{version}"
                if component_id in self.index:
                    del self.index[component_id]
                    
                    # Remove files
                    component_dir = self.components_dir / name / version
                    if component_dir.exists():
                        shutil.rmtree(component_dir)
                    
                    self._save_index()
                    print(f"✓ Unregistered: {component_id}")
                    return True
            else:
                # Unregister all versions
                to_remove = [
                    cid for cid in self.index.keys()
                    if cid.startswith(f"{name}@")
                ]
                
                for cid in to_remove:
                    del self.index[cid]
                
                # Remove directory
                component_dir = self.components_dir / name
                if component_dir.exists():
                    shutil.rmtree(component_dir)
                
                self._save_index()
                print(f"✓ Unregistered all versions of: {name}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Failed to unregister component: {e}")
            return False
    
    def get(self, name: str, version: Optional[str] = None) -> Optional[ComponentMetadata]:
        """Get component metadata"""
        if version:
            return self.index.get(f"{name}@{version}")
        else:
            # Get latest version
            versions = [
                meta for cid, meta in self.index.items()
                if cid.startswith(f"{name}@")
            ]
            if versions:
                return max(versions, key=lambda m: semver.parse(m.version))
        return None
    
    def list_components(self, component_type: Optional[ComponentType] = None) -> List[ComponentMetadata]:
        """List all components"""
        components = list(self.index.values())
        if component_type:
            components = [c for c in components if c.type == component_type]
        return sorted(components, key=lambda c: (c.name, c.version))
    
    def search(self, query: str) -> List[ComponentMetadata]:
        """Search components by name or keywords"""
        query_lower = query.lower()
        results = []
        
        for meta in self.index.values():
            if (query_lower in meta.name.lower() or
                query_lower in meta.description.lower() or
                any(query_lower in kw.lower() for kw in meta.keywords)):
                results.append(meta)
        
        return results
    
    def get_component_dir(self, name: str, version: str) -> Path:
        """Get component directory"""
        return self.components_dir / name / version


class DependencyResolver:
    """Resolves component dependencies"""
    
    def __init__(self, registry: ComponentRegistry):
        self.registry = registry
    
    def resolve(self, component: ComponentMetadata) -> Tuple[bool, List[ComponentMetadata], List[str]]:
        """
        Resolve component dependencies
        
        Returns:
            (success, resolved_deps, errors)
        """
        resolved = []
        errors = []
        visited = set()
        
        def resolve_recursive(comp: ComponentMetadata):
            comp_id = comp.get_id()
            if comp_id in visited:
                return
            visited.add(comp_id)
            
            for dep in comp.dependencies:
                # Find installed version that satisfies constraint
                installed = self.registry.get(dep.name)
                
                if not installed:
                    if not dep.optional:
                        errors.append(f"Missing required dependency: {dep.name} {dep.version_constraint}")
                    continue
                
                if not dep.is_satisfied_by(installed.version):
                    errors.append(
                        f"Dependency version mismatch: {dep.name} "
                        f"(required: {dep.version_constraint}, found: {installed.version})"
                    )
                    continue
                
                resolved.append(installed)
                resolve_recursive(installed)
        
        resolve_recursive(component)
        
        return len(errors) == 0, resolved, errors
    
    def get_install_order(self, components: List[ComponentMetadata]) -> List[ComponentMetadata]:
        """Get installation order based on dependencies"""
        # Topological sort
        installed = set()
        result = []
        
        def visit(comp: ComponentMetadata):
            comp_id = comp.get_id()
            if comp_id in installed:
                return
            
            # Visit dependencies first
            for dep in comp.dependencies:
                dep_comp = self.registry.get(dep.name)
                if dep_comp:
                    visit(dep_comp)
            
            result.append(comp)
            installed.add(comp_id)
        
        for comp in components:
            visit(comp)
        
        return result


class ComponentMarketplace:
    """Component marketplace client"""
    
    def __init__(self, marketplace_url: str = "https://marketplace.plhub.dev"):
        self.marketplace_url = marketplace_url
    
    def search(self, query: str, component_type: Optional[ComponentType] = None) -> List[Dict]:
        """Search marketplace for components"""
        try:
            params = {'q': query}
            if component_type:
                params['type'] = component_type.value
            
            response = requests.get(
                f"{self.marketplace_url}/api/search",
                params=params,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            print(f"Marketplace search failed: {e}")
        
        return []
    
    def get_component(self, name: str, version: Optional[str] = None) -> Optional[Dict]:
        """Get component details from marketplace"""
        try:
            url = f"{self.marketplace_url}/api/components/{name}"
            if version:
                url += f"/{version}"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            
        except Exception as e:
            print(f"Failed to fetch component: {e}")
        
        return None
    
    def download(self, name: str, version: str, dest_dir: Path) -> bool:
        """Download component from marketplace"""
        try:
            url = f"{self.marketplace_url}/api/components/{name}/{version}/download"
            
            response = requests.get(url, stream=True, timeout=30)
            
            if response.status_code == 200:
                # Download as zip
                zip_file = dest_dir / f"{name}-{version}.zip"
                dest_dir.mkdir(parents=True, exist_ok=True)
                
                with open(zip_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Extract
                import zipfile
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(dest_dir)
                
                zip_file.unlink()  # Remove zip file
                
                print(f"✓ Downloaded: {name}@{version}")
                return True
            
        except Exception as e:
            print(f"Download failed: {e}")
        
        return False
    
    def publish(self, component_dir: Path, metadata: ComponentMetadata, api_key: str) -> bool:
        """Publish component to marketplace"""
        try:
            # Create zip archive
            import zipfile
            import tempfile
            
            with tempfile.NamedTemporaryFile(suffix='.zip', delete=False) as tmp:
                with zipfile.ZipFile(tmp.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    for file_rel in metadata.files:
                        file_path = component_dir / file_rel
                        if file_path.exists():
                            zipf.write(file_path, file_rel)
                    
                    # Add metadata
                    metadata_json = json.dumps(metadata.to_dict(), indent=2)
                    zipf.writestr('component.json', metadata_json)
                
                # Upload
                with open(tmp.name, 'rb') as f:
                    files = {'file': f}
                    headers = {'Authorization': f'Bearer {api_key}'}
                    
                    response = requests.post(
                        f"{self.marketplace_url}/api/publish",
                        files=files,
                        headers=headers,
                        timeout=60
                    )
                    
                    if response.status_code == 201:
                        print(f"✓ Published: {metadata.get_id()}")
                        return True
                    else:
                        print(f"Publish failed: {response.text}")
            
        except Exception as e:
            print(f"Publish error: {e}")
        
        return False


class ComponentManager:
    """High-level component management"""
    
    def __init__(self, plhub_root: Path):
        self.plhub_root = plhub_root
        self.registry = ComponentRegistry(plhub_root / "components")
        self.resolver = DependencyResolver(self.registry)
        self.marketplace = ComponentMarketplace()
    
    def install(self, name: str, version: Optional[str] = None, 
               source: str = "marketplace") -> bool:
        """Install a component"""
        print(f"Installing {name}" + (f"@{version}" if version else ""))
        
        if source == "marketplace":
            # Download from marketplace
            if not version:
                # Get latest version
                info = self.marketplace.get_component(name)
                if not info:
                    print(f"Component not found: {name}")
                    return False
                version = info['version']
            
            # Download
            temp_dir = self.plhub_root / "temp" / f"{name}-{version}"
            if not self.marketplace.download(name, version, temp_dir):
                return False
            
            # Load metadata
            metadata_file = temp_dir / "component.json"
            metadata = ComponentMetadata.from_dict(json.loads(metadata_file.read_text()))
            
        else:
            # Install from local directory
            source_dir = Path(source)
            metadata_file = source_dir / "component.json"
            
            if not metadata_file.exists():
                print(f"No component.json found in {source}")
                return False
            
            metadata = ComponentMetadata.from_dict(json.loads(metadata_file.read_text()))
            temp_dir = source_dir
        
        # Resolve dependencies
        print("Resolving dependencies...")
        success, deps, errors = self.resolver.resolve(metadata)
        
        if not success:
            print("Dependency resolution failed:")
            for error in errors:
                print(f"  - {error}")
            return False
        
        # Install dependencies first
        for dep_meta in deps:
            if not self.registry.get(dep_meta.name, dep_meta.version):
                print(f"Installing dependency: {dep_meta.name}@{dep_meta.version}")
                if not self.install(dep_meta.name, dep_meta.version):
                    return False
        
        # Register component
        return self.registry.register(metadata, temp_dir)
    
    def uninstall(self, name: str, version: Optional[str] = None) -> bool:
        """Uninstall a component"""
        return self.registry.unregister(name, version)
    
    def list_installed(self, component_type: Optional[ComponentType] = None) -> List[ComponentMetadata]:
        """List installed components"""
        return self.registry.list_components(component_type)
    
    def search(self, query: str, source: str = "local") -> List:
        """Search for components"""
        if source == "marketplace":
            return self.marketplace.search(query)
        else:
            return self.registry.search(query)
    
    def update(self, name: str) -> bool:
        """Update component to latest version"""
        # Get current version
        current = self.registry.get(name)
        if not current:
            print(f"Component not installed: {name}")
            return False
        
        # Check marketplace for updates
        latest_info = self.marketplace.get_component(name)
        if not latest_info:
            print(f"Component not found in marketplace: {name}")
            return False
        
        latest_version = latest_info['version']
        
        if semver.compare(latest_version, current.version) <= 0:
            print(f"Already at latest version: {current.version}")
            return True
        
        print(f"Updating {name}: {current.version} → {latest_version}")
        
        # Uninstall old version
        self.uninstall(name, current.version)
        
        # Install new version
        return self.install(name, latest_version)
    
    def check_updates(self) -> List[Tuple[str, str, str]]:
        """Check for component updates"""
        updates = []
        
        for meta in self.registry.list_components():
            latest_info = self.marketplace.get_component(meta.name)
            if latest_info:
                latest_version = latest_info['version']
                if semver.compare(latest_version, meta.version) > 0:
                    updates.append((meta.name, meta.version, latest_version))
        
        return updates
    
    def publish(self, component_dir: Path, api_key: str) -> bool:
        """Publish component to marketplace"""
        metadata_file = component_dir / "component.json"
        
        if not metadata_file.exists():
            print("No component.json found")
            return False
        
        metadata = ComponentMetadata.from_dict(json.loads(metadata_file.read_text()))
        
        return self.marketplace.publish(component_dir, metadata, api_key)


def create_component_template(name: str, component_type: ComponentType, 
                             output_dir: Path) -> bool:
    """Create a new component template"""
    try:
        component_dir = output_dir / name
        component_dir.mkdir(parents=True, exist_ok=True)
        
        # Create metadata
        metadata = ComponentMetadata(
            name=name,
            version="1.0.0",
            type=component_type,
            author="Your Name",
            description=f"A {component_type.value} component",
            keywords=[component_type.value],
            files=["README.md", f"{name}.poh"]
        )
        
        # Write metadata
        metadata_file = component_dir / "component.json"
        metadata_file.write_text(json.dumps(metadata.to_dict(), indent=2))
        
        # Create README
        readme = component_dir / "README.md"
        readme.write_text(f"""# {name}

{metadata.description}

## Installation

```bash
plhub component install {name}
```

## Usage

```poh
Start Program
# Your code here
End Program
```

## License

MIT
""")
        
        # Create main file
        main_file = component_dir / f"{name}.poh"
        main_file.write_text("""Start Program

# Component implementation

End Program
""")
        
        print(f"✓ Created component template: {component_dir}")
        return True
        
    except Exception as e:
        print(f"Failed to create template: {e}")
        return False
