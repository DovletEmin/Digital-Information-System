This folder holds wheels used for offline builds.

To add missing wheels (for example `psycopg2-binary`), run the helper script:

```bash
python scripts/download_wheels.py psycopg2-binary==2.9.11
```

After the wheel appears here, `docker build` will be able to install from `wheelhouse`.

Notes:

- If a wheel for your platform/version does not exist on PyPI, you may need to build from source (requires `libpq-dev` and a compiler) or choose a different package version.
- For reproducible builds, keep the wheel files checked into `wheelhouse/` or provide an internal package index.
