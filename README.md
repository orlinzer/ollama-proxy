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

```bash
source .env/bin/activate
python src/main.py
```

You can connect open-webui to the proxy server by loading it like this:

```bash
sudo docker run -p 8080:8080 -e 'OLLAMA_BASE_URL=http://localhost:5000' dyrnq/open-webui
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
