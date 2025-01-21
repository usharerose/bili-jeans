# bili-jeans

![license](https://img.shields.io/github/license/usharerose/bili-jeans)
![badge](https://img.shields.io/endpoint?url=https://gist.githubusercontent.com/usharerose/37bd5abc9fe5172ec6df11ce899f2f3b/raw/badge.json)

Download available resources from Bilibili

## Development

### Docker (Recommended)
Execute the following commands, which sets up a service with development dependencies and enter into it.
```shell
> make run && make ssh
```

### Virtual Environment
1. As a precondition, please [install Poetry](https://python-poetry.org/docs/1.7/#installation) which is a tool for dependency management and packaging in Python.
2. Install and activate local virtual environment
    ```shell
    > poetry install && poetry shell
    ```
3. `IPython` is provided as interactive shell
