<p align="center">
    <img src="./media/picklevw.png" width="200px"/>
</p>
<div align="center"
    
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/jonathanciapetti/picklevw)
![workflow](https://github.com/jonathanciapetti/picklevw/actions/workflows/python-app.yaml/badge.svg)
[![codecov](https://codecov.io/github/jonathanciapetti/picklevw/graph/badge.svg?token=UCDTWBNL7A)](https://codecov.io/github/jonathanciapetti/picklevw)
![version](https://img.shields.io/badge/version-1.4.6-blue)

</div>

**picklevw** (pronounced *pickleview*) is a simple Python web application, designed to read and display pickle files
using `pandas` and `streamlit`.

Try it live on [picklevw.streamlit.app](https://picklevw.streamlit.app)

### Getting Started

---

#### Installation

Clone the repository and install the required dependencies (possibly on a virtual environment):

```console
git clone https://github.com/jonathanciapetti/picklevw.git
cd picklevw
python3 -m venv ./venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Running the App

To start the application, run:

```console
streamlit run src/picklevw.py
```

Here's a screenshot of the app displaying the unpickled content of a legit pickle:
<p>
    <img src="./media/screenshot_1.png" width="100%" alt="legit pickle">
</p>

---

### Safetey checks

`picklevw` relies on [`Fickling`](https://github.com/trailofbits/fickling) to detect potentially malicious pickles. `fickling` depends on [`distutils`](https://docs.python.org/3/library/distutils.html) which is only available up to Python 3.11. Therefore, Python 3.11 is the latest version that `picklevw` supports.

### Contributing

Contributions are <ins>**welcome**</ins>! If you have any ideas, suggestions, or bug reports, please open an issue or
submit a pull request.

### License

This project is licensed under the MIT License - see the LICENSE.txt file for details.

### Contacts

- Repo: [https://github.com/jonathanciapetti/picklevw](https://github.com/jonathanciapetti/picklevw)
- Email: [jonathan.ciapetti@normabytes.com](mailto:jonathan.ciapetti@normabytes.com)
