[//]: # (![Static Badge]&#40;https://img.shields.io/badge/build-passed-green&#41;)

<p align="center">
    <img src="./logo/picklevw_logo_and_name.png" />
</p>

<div align="center" style="display: flex; justify-content: center;">

![workflow](https://github.com/jonathanciapetti/picklevw/actions/workflows/python-app.yml/badge.svg)
![version](https://img.shields.io/badge/version-0.0.0-blue)

</div>


<!-- ![logo](./logo/picklevw_logo.png) -->

<br />

**picklevw** (pronunced *pickleview*) is a small desktop Python application, designed to read and display pickle files using Pandas and Tkinter.
It's basically a GUI wrapping `pandas.read_pickle()`.

<br />

### ✨ Features

- User-friendly: simple and intuitive GUI built with Tkinter.
- Fast: efficiently reads pickle files using Pandas.
- No freezing GUI: GUI and data live in different processes.

---

### 🚀 Getting Started

#### Installation

Clone the repository and install the required dependencies:

```bash
git clone https://github.com/yourusername/picklevw.git
cd picklevw
pip install -r requirements.txt
```
#### Running the App

To start the application, run:

```bash
python3 picklevw.py
```

#### 🛠️ Dependencies
- *pandas* >= 1.5
- *tkinter* (usually included with Python installations)
- *prettyprinter*

#### ⌛ TODOs
- GUI testing: testing on `xvfb` using `pyvirtualdisplay`
- Testing of pickles' life cycle.

---

### 🤝 Contributing
Contributions are <ins>**welcome**</ins>! If you have any ideas, suggestions, or bug reports, please open an issue or submit a pull request.


### 📜 License
This project is licensed under the MIT License - see the LICENSE file for details.

### 📫 Contacts
- Repo: [https://github.com/jonathanciapetti/picklevw](https://github.com/jonathanciapetti/picklevw)
- Email: [jonathan.ciapetti@normabytes.com](mailto:jonathan.ciapetti@normabytes.com)
