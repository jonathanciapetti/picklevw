UI = {
    "title": "picklevw",
    "icon": "🥒",
    "layout": "wide",
    "logo_size": "large",
    "file_extensions": [".pkl", ".pickle", ".gz"],
    "PICKLE_DOCS_URL": "https://docs.python.org/3/library/pickle.html",
}

MESSAGES = {
    "setup_page_html": (
        """
        <p style="font-size: 20px; display: inline; text-align: bottom;">
        A simple <a href="{url}" target="_blank">Pickle</a> file viewer. MIT Licensed.
        </p>
        <span class="is-badge" style="background-color: rgba(128, 132, 149, 0.1); color: rgb(85, 88, 103); font-size: 1rem; padding-left: 0.4375rem; padding-right: 0.4375rem; border-radius: 0.4375rem; font-weight: bold;">{version}</span>
        """
    ),
    "UPLOAD_PROMPT": "Upload a Pickle (.pkl, .pickle) or Gzip-Pickle (.gz) File",
    "GENERIC_LOAD_ERROR": "picklevw could not read the content of this file.",
    "NOT_JSON_WARNING": "The object is not JSON serializable and is not a DataFrame.",
    "UNSAFE_WARNING": "⚠️ You have enabled unsafe loading for DataFrames. Malicious code might be executed.",
    "row_col_summary": "Readable: **{rows}** rows and **{cols}** columns",
    "TOGGLER_HELP": "WARNING: Enabling this may allow execution of untrusted code if the uploaded file is malicious.",
    "TOGGLER_TEXT": "Bypass safety check for Pandas and NumPy data (unsafe)",
    "CONTENT_DISPLAY": "**Content**",
    "CHART": "**Chart**",
    "POTENTIAL_THREAT":  "A potential **threat** has been detected in this file. Stopped loading.",
}

CONFIG = {
    "version": "v1.3.0",
    "always_disallow_unsafe": False,
    "allow_unsafe": False,
    "max_limit": None,
}
