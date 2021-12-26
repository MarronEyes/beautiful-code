# Beautiful Code

Here is the source code of "Beautiful Code". It is a small tool that can generate images with your code in it.
### Build
First, **create a new virtual environment !** Beautiful Code needs a specific version of pygments from this [fork](https://github.com/MarronEyes/pygments).
(replace python3 with py if you are on Windows)
```
python3 -m venv /path/to/venv
```
Make sure you have the latest version of [build](https://github.com/pypa/build)
```console
python3 -m pip install --upgrade build
```
And run this command from the project directory 
```console
python3 -m build
```

### Usage
Simply run ``__main__.py`` and open your browser to localhost:8080 !
Or if you want to test image_code.py, there is no way to run it **yet** in CLI. This will be added in a new version of the project.

### Development
The project is still in development and there are many bugs.But if you want to contribute to it, here is the steps:
1. Fork the project
2. Create your branch with the name of your feature
3. Commit your changes
4. Push them to your branch
5. Create a new pull request

### License
The code is licensed under MIT License. See LICENSE for more informations.