[//]: # (![Static Badge]&#40;https://img.shields.io/badge/build-passed-green&#41;)

<p align="center">
    <img src="./logo/picklevw_logo_and_name.png" height="100px"/>
</p>

<div align="center" style="display: flex; justify-content: center;">

![workflow](https://github.com/jonathanciapetti/picklevw/actions/workflows/python-app.yml/badge.svg)
[![codecov](https://codecov.io/github/jonathanciapetti/picklevw/graph/badge.svg?token=UCDTWBNL7A)](https://codecov.io/github/jonathanciapetti/picklevw)
![version](https://img.shields.io/badge/version-0.2.0-blue)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>


<!-- ![logo](./logo/picklevw_logo.png) -->

<br />

**picklevw** (pronunced *pickleview*) is a small desktop Python application, designed to read and display pickle files using Pandas and Tkinter.
It's basically a GUI wrapping `pandas.read_pickle()`.

<br />

### Features

- User-friendly: simple and intuitive GUI built with Tkinter.
- Fast: efficiently reads pickle files using Pandas.
- No freezing GUI: GUI and data live in different processes.

---

### Getting Started

#### Installation

Clone the repository and install the required dependencies (possibly on a virtual environment):

```console
git clone https://github.com/yourusername/picklevw.git
cd picklevw
pip install -r requirements.txt
```

| OS      | Compatible |
|---------|-----------:|
| Linux   |        yes |
| Windows |         no |
| macOS   |         no |

#### Running the App

To start the application, run:

```console
python3 picklevw.py
```

#### Dependencies
- Python >= 3.10
- Pandas >= 1.5
- Tkinter (usually included with Python installations)
- Prettyprinter

#### TODOs
- GUI testing: testing on `xvfb` using `pyvirtualdisplay`
- Print of whole long pickles, through paging.
- Integration with [Fickling](https://github.com/trailofbits/fickling).

---

### Contributing
Contributions are <ins>**welcome**</ins>! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.


### License
This project is licensed under the MIT License - see the LICENSE file for details.

### Contacts
- Repo: [https://github.com/jonathanciapetti/picklevw](https://github.com/jonathanciapetti/picklevw)
- Email: [jonathan.ciapetti@normabytes.com](mailto:jonathan.ciapetti@normabytes.com)
