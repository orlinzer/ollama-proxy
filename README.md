# Ollama Proxy

## Description

A simple proxy server for Ollama that allows you to use the Ollama API with a custom URL.
It provides a way to set pre and post prompts for the API requests and responses, and it can be used with open-webui or other applications that require a custom Ollama API endpoint.

## License

This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for details.

## Prerequisites

- Ubuntu system
- Ollama
- git

## Setup

```bash
git clone https://github.com/orlinzer/ollama-proxy.git
cd ollama-proxy
sudo ./scripts/setup.sh
```

## Usage

To start the proxy server, run:

- **Linux:**

  ```bash
  source .venv/bin/activate
  scripts/run.sh
  ```

- **Windows:**

  ```bat
  source .venv\Scripts\activate
  scripts\run.bat
  ```

You can connect open-webui to the proxy server by loading it like this:

### Local

- **Linux:**

  ```bash
  ./scripts/run_ui.sh
  ```

- **Windows:**

  ```bat
  .\scripts\run_ui.bat
  ```

### Docker

- **Linux:**

  ```bash
  sudo docker run -p 8080:8080 -e 'OLLAMA_BASE_URL=http://172.17.0.1:5000' dyrnq/open-webui
  ```

- **Windows:**

  ```bat
  sudo docker run -p 8080:8080 -e 'OLLAMA_BASE_URL=http://host.docker.internal:5000' dyrnq/open-webui
  ```

## Configuration

You can configure the proxy server by editing the `.env` file or by setting environment variables. The following variables are available:

- **OLLAMA_HOST:**

  _default:_ http://localhost:11434

- **PORT:**

  _default:_ 5000

- **PRE_PROMPT:**

  _default:_ Please answer as concisely as possible:

- **POST_PROMPT:**

  _default:_ Thank you.\nRemember to answer in JSON format.

- **ENABLE_INPUT_GARD:**

  _default:_ true

- **ENABLE_OUTPUT_GARD:**

  _default:_ true

- **PRINT_USER_PROMPT:**

  _default:_ true

- **PRINT_WRAPPED_PROMPT:**

  _default:_ true
