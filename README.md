# Jinjagen 🌀

**A CLI tool for generating files using Jinja2 templates with smart delimiters and dynamic data.**

## Features ✨

- **Auto-detects delimiters** for code/file types (e.g., `#` for Python/Shell, `/*%` for C/JS).
- **Supports JSON/YAML** data inputs for dynamic templates.
- **Lightweight CLI** with stdin/stdout support.

## ☕ Support

If you find this project helpful, consider supporting me:

## [![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/B0B01E8SY7)

## Usage 🛠️

### Basic Example

Generate a file from a template and JSON data:

```bash
python -m jinjagen template.txt.j2 output.txt -d data.json
```

### Real-World Use Case: **Bash Script Generation**

**1. Template (`backup.sh.j2`)**:

```bash
#!/bin/bash
#jinjagen: -D#
BACKUP_PATHS=(#% for path in backup_paths %# "#{ path }#" #% endfor %#)

#% if notify.enabled %#
EMAIL="#{ notify.email }#"
#% endif %#
```

**2. Data (`config.json`)**:

```json
{
  "backup_paths": ["/home/user/docs", "/etc/nginx"],
  "notify": { "enabled": true, "email": "admin@example.com" }
}
```

**3. Generate Script**:

```bash
python -m jinjagen backup.sh.j2 backup.sh -d config.json
```

**Output (`backup.sh`)**:

```bash
#!/bin/bash
BACKUP_PATHS=( "/home/user/docs"  "/etc/nginx" )
EMAIL="admin@example.com"
```

---

## Advanced Options ⚙️

| Flag              | Description                          | Example                      |
| ----------------- | ------------------------------------ | ---------------------------- |
| `-d/--data FILE`  | Load variables from JSON/YAML.       | `-d config.yml`              |
| `-D/--delimiters` | Force delimiters (`#`, `/`, or `.`). | `-D#` (for Bash/Python)      |
| `-t/--templates`  | Specify template directory.          | `-t ./templates`             |
| `INPUT - OUTPUT`  | Use `-` for stdin/stdout.            | `template.j2 - -d data.json` |

---

## Delimiters Explained 🔠

Jinjagen automatically adapts Jinja2 delimiters to avoid conflicts with different file types. You can also override this behavior manually.

### Default Behavior (Auto-Detection)

The tool guesses delimiters based on file extensions:

| File Type         | Example Extensions    | Delimiters                                  |
| ----------------- | --------------------- | ------------------------------------------- |
| **C/JS/Java**     | `.c`, `.js`, `.java`  | `/*% %*/` (blocks)<br>`/*{ }*/` (variables) |
| **Python/Shell**  | `.py`, `.sh`, `.yaml` | `#% %#` (blocks)<br>`#{ }#` (variables)     |
| **Generic/Other** | `.txt`, `.html`       | `{% %}` (blocks)<br>`{{ }}` (variables)     |

_Example: For a `.c` file, Jinjagen uses `/_% if x %_/`instead of`{% if x %}`._

### Manual Override

Force specific delimiters with `-D/--delimiters`:

```bash
# Use #-style (for Python/Shell)
python -m jinjagen template.txt output.txt -D#

# Use /-style (for C/JS)
python -m jinjagen template.c output.c -D/

# Use default Jinja2 delimiters (.)
python -m jinjagen template.html output.html -D.
```

### Custom Delimiter Logic

The delimiter system handles these cases:

1. **Conflict Prevention**:  
   Avoids syntax clashes (e.g., `{{ }}` in Vue.js or `{% %}` in Django).
2. **Comment Safety**:  
   Respects language comment styles (e.g., `#` in Bash won’t break `#%` blocks).
3. **Edge Cases**:  
   If no extension matches (or for `.txt`), falls back to standard Jinja2 delimiters.

---

## Practical Usage 🛠️

Jinjagen shines in generating configs, scripts, and code files. Here are common scenarios:

### 1. Generate Config Files

**Scenario**: Create an `nginx.conf` with dynamic ports and SSL settings.  
**Template (`nginx.conf.j2`)**:

```nginx
#jinjagen: -D#
server {
  listen #{ port }#;
  server_name #{ domain }#;

  #% if ssl_enabled %#
  ssl_certificate #{ ssl_cert }#;
  ssl_certificate_key #{ ssl_key }#;
  #% endif %#
}
```

**Data (`deploy.yml`)**:

```yaml
port: 443
domain: "example.com"
ssl_enabled: true
ssl_cert: "/etc/ssl/certs/example.crt"
ssl_key: "/etc/ssl/private/example.key"
```

**Command**:

```bash
python -m jinjagen nginx.conf.j2 nginx.conf -d deploy.yml
```

---

### 2. Dynamic Script Generation

**Scenario**: Create a backup script with conditional email alerts.  
**Template (`backup.sh.j2`)**:

```bash
#!/bin/bash
#jinjagen: -D#
BACKUP_DIRS=(#% for dir in backup_dirs %# "#{ dir }#" #% endfor %#)

#% if notify %#
echo "Backup done" | mail -s "Backup Log" #{ email }#
#% endif %#
```

**Data (`config.json`)**:

```json
{
  "backup_dirs": ["/home", "/etc"],
  "notify": true,
  "email": "admin@example.com"
}
```

**Command**:

```bash
python -m jinjagen backup.sh.j2 backup.sh -d config.json -D#
```

---

### 3. CI/CD Pipeline Integration

**Scenario**: Generate environment-specific `.env` files during deployment.  
**Template (`.env.j2`)**:

```ini
#jinjagen: -D.
DB_HOST=#{ db_host }#
DB_USER=#{ db_user }#
#% if env == "prod" %#
DB_PASSWORD=#{ "vault.get('db_prod_pass')" }#
#% else %#
DB_PASSWORD=devpass
#% endif %#
```

**Command** (using environment variables):

```bash
python -m jinjagen .env.j2 .env -D# -d <(echo '{"env":"prod","db_host":"10.0.0.1","db_user":"admin"}')
```

---

### 4. Code Generation

**Scenario**: Generate a Python class from a template.  
**Template (`model.py.j2`)**:

```python
#jinjagen: -D#
class #{ class_name }#:
    def __init__(self):
        #% for field in fields %#
        self.#{ field }# = None
        #% endfor %#
```

**Data (`model.json`)**:

```json
{
  "class_name": "UserModel",
  "fields": ["id", "name", "email"]
}
```

**Command**:

```bash
python -m jinjagen model.py.j2 UserModel.py -d model.json
```

---

### Pro Tips 💡

- **Use `-` for stdin/stdout**: Pipe templates/data between tools.
  ```bash
  echo "Hello #{ name }#" | python -m jinjagen -D# - -d <(echo '{"name":"World"}')
  ```
- **Override delimiters** when auto-detection fails:
  ```bash
  python -m jinjagen template.sql output.sql -D/  # Force /*% style for SQL
  ```
- **Template directories**: Use `-t ./templates` to enable `{% include %}`.

---
