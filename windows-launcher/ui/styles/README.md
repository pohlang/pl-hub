# UI Styles

This directory stores theme definitions used by PLHub.

- `active_style.json` selects the theme currently applied to the project.
- `themes/` contains editable JSON themes.

Manage themes via the CLI:

```bash
python plhub.py style list
python plhub.py style apply default_light
python plhub.py style create My Theme --base default_light
```
