# Installation of dependencies
## Ollama
[Ollama](https://ollama.com) is used for downloading and serving a large number of llm packages. To install it follow the instructions given here https://ollama.com/download. If you are on linux and your Ollama is available in your distro's repository then you can install it through distro's package manager and set up a systemd service. For Arch linux the steps would be

```[bash]
$ sudo pacman -S ollama
```

Then create the file /home/usr/.config/systemd/user/ollama.service with the content
```[bash]
[Unit]
Description=Ollama Serve
After=network-online.target

[Service]
ExecStart=/usr/bin/ollama serve
Restart=always
RestartSec=3

[Install]
WantedBy=default.target
```

Then run
```[bash]
$ systemctl --user enable ollama.service 
$ systemctl --user start ollama.service 
```

## Python packages
To create the python environment do
```[bash]
pyenv virtualenv 3.8 ganga-ai8
pyenv activate ganga-ai8
pip install -r requirements.txt
```

# Running the code
To run the code do
```[bash]
$ ipython
$ %load_ext ganga-ai
```
