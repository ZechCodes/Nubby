# Examples

This page provides practical examples of using Nubby in different scenarios.

## Basic Configuration Example

This example shows a basic application configuration setup:

```python
from dataclasses import dataclass
from bevy import inject, dependency
from nubby.models import new_file_model

# Define a configuration file
app_config = new_file_model("app_config")

@app_config.section("app")
@dataclass
class AppConfig:
    name: str
    version: str
    debug: bool = False

@app_config.section("database")
@dataclass
class DatabaseConfig:
    host: str
    port: int
    username: str
    password: str
    database: str

# Use the configuration
@inject
def initialize_app(app_cfg: AppConfig = dependency()):
    print(f"Initializing {app_cfg.name} v{app_cfg.version}")
    if app_cfg.debug:
        print("Debug mode enabled")

@inject
def setup_database(db_cfg: DatabaseConfig = dependency()):
    connection_string = f"postgresql://{db_cfg.username}:{db_cfg.password}@{db_cfg.host}:{db_cfg.port}/{db_cfg.database}"
    print(f"Connecting to database: {connection_string}")
    # ... database connection logic ...

# Run the application
if __name__ == "__main__":
    initialize_app()
    setup_database()
```

Example `app_config.json`:

```json
{
  "app": {
    "name": "MyApp",
    "version": "1.0.0",
    "debug": true
  },
  "database": {
    "host": "localhost",
    "port": 5432,
    "username": "user",
    "password": "password",
    "database": "myapp"
  }
}
```

## Web Application Example

This example shows how to use Nubby in a web application:

```python
from dataclasses import dataclass
from bevy import inject, dependency
from nubby.models import new_file_model
from flask import Flask

# Define a configuration file
web_config = new_file_model("web_config")

@web_config.section("server")
@dataclass
class ServerConfig:
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False

@web_config.section("security")
@dataclass
class SecurityConfig:
    secret_key: str
    token_expiration: int = 3600  # seconds

# Create a Flask application
app = Flask(__name__)

# Configure the application
@inject
def configure_app(server_cfg: ServerConfig = dependency(),
                 security_cfg: SecurityConfig = dependency()):
    app.config["DEBUG"] = server_cfg.debug
    app.config["SECRET_KEY"] = security_cfg.secret_key
    return app

# Define routes
@app.route("/")
def index():
    return "Hello, World!"

# Run the application
if __name__ == "__main__":
    app = configure_app()
    app.run(host=app.config.get("HOST", "127.0.0.1"),
            port=app.config.get("PORT", 5000))
```

Example `web_config.yaml`:

```yaml
server:
  host: 0.0.0.0
  port: 8080
  debug: true

security:
  secret_key: my-secret-key
  token_expiration: 7200
```

## CLI Application Example

This example shows how to use Nubby in a CLI application:

```python
import argparse
from dataclasses import dataclass
from bevy import inject, dependency
from nubby.models import new_file_model
from nubby import get_active_controller

# Define a configuration file
cli_config = new_file_model("cli_config")

@cli_config.section("defaults")
@dataclass
class DefaultConfig:
    output_dir: str = "./output"
    verbose: bool = False
    format: str = "json"

# Create a CLI application
def create_parser():
    parser = argparse.ArgumentParser(description="Example CLI application")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument("--format", choices=["json", "yaml", "csv"], help="Output format")
    return parser

@inject
def run_cli(defaults: DefaultConfig = dependency()):
    parser = create_parser()
    args = parser.parse_args()
    
    # Override defaults with command line arguments
    output_dir = args.output_dir or defaults.output_dir
    verbose = args.verbose or defaults.verbose
    format = args.format or defaults.format
    
    if verbose:
        print(f"Output directory: {output_dir}")
        print(f"Format: {format}")
    
    # ... application logic ...

# Run the application
if __name__ == "__main__":
    run_cli()
```

Example `cli_config.toml`:

```toml
[defaults]
output_dir = "/tmp/output"
verbose = true
format = "yaml"
```

## Multiple Configuration Files Example

This example shows how to use multiple configuration files:

```python
from dataclasses import dataclass
from bevy import inject, dependency
from nubby.models import new_file_model
from nubby import get_active_controller

# Define configuration files
app_config = new_file_model("app_config")
user_config = new_file_model("user_config")

@app_config.section("app")
@dataclass
class AppConfig:
    name: str
    version: str

@app_config.section("logging")
@dataclass
class LoggingConfig:
    level: str = "INFO"
    file: str = "app.log"

@user_config.section("preferences")
@dataclass
class UserPreferences:
    theme: str = "light"
    language: str = "en"

# Add search paths
get_active_controller().add_path("./config")  # For app_config
get_active_controller().add_path("~/.config/myapp")  # For user_config

# Use the configuration
@inject
def initialize_app(app_cfg: AppConfig = dependency(),
                  log_cfg: LoggingConfig = dependency()):
    print(f"Initializing {app_cfg.name} v{app_cfg.version}")
    print(f"Logging to {log_cfg.file} with level {log_cfg.level}")

@inject
def setup_user_interface(prefs: UserPreferences = dependency()):
    print(f"Setting up UI with theme {prefs.theme} and language {prefs.language}")

# Run the application
if __name__ == "__main__":
    initialize_app()
    setup_user_interface()
```
