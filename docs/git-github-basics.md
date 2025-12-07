# Git & GitHub Basics

## 1. Setting Up a GitHub Repository

1. Log in to GitHub.
2. Click **New Repository**.
3. Choose:
   - **Repository name**
   - Public or private
   - Optionally add: README, .gitignore, LICENSE
4. Click **Create Repository**.
5. Copy the repository URL (SSH or HTTPS).

---

## 2. Initializing a Local Folder, Adding Files, Committing, and Pushing

### Create and initialize the project locally
```bash
mkdir myproject
cd myproject
git init
```

### Add your GitHub repo as the remote origin
```bash
git remote add origin <your-repo-url>
```

### Add files
```bash
git add file1.py file2.md
```

### Commit your changes
```bash
git commit -m "Initial commit"
```

### Push to GitHub
```bash
git push -u origin main
```

If GitHub created the repo with a README/.gitignore, your first push may be rejected.  
Fix by pulling those commits:

```bash
git pull origin main --rebase
git push origin main
```

---

## 3. Adding Folders, New Files, and Moving Things Around

### Adding a new folder
Just create it normally via GUI or terminal:
```bash
mkdir docs
```

Git does **not** track folders automatically — only files.

Add files inside, then:
```bash
git add docs/
git commit -m "Add docs folder"
git push origin main
```

### Adding a new file
```bash
git add newfile.md
git commit -m "Add newfile.md"
git push origin main
```

### Moving a file
If you move a file:
```bash
git mv oldname.md docs/newname.md
git commit -m "Move file into docs/"
git push origin main
```

If you moved it manually (GUI), Git sees a delete + new file:
```bash
git add -A
git commit -m "Move files"
git push origin main
```

### Important notes
- `git commit -a` **does NOT commit untracked files**.
- Always run `git status` to see what Git is tracking.
- If a push is rejected, run:
  ```bash
  git pull origin main --rebase
  git push origin main
  ```

---

This guide covers the basics needed for solo developers working with Git and GitHub.
