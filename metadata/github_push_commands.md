# GitHub Push Commands

Use these commands after creating an empty GitHub repository.

Replace `<YOUR_GITHUB_ACCOUNT>` and `<REPOSITORY_NAME>` with the actual target.

```bash
cd path/to/release_repo
git init
git add .
git commit -m "Release reproducibility package for municipal service data privacy-risk engineering"
git branch -M main
git remote add origin https://github.com/<YOUR_GITHUB_ACCOUNT>/<REPOSITORY_NAME>.git
git push -u origin main
```

After pushing, copy the final repository URL into the manuscript data availability statement and replace any remaining repository placeholders.

Recommended repository name:

```text
municipal-service-privacy-risk-engineering
```
