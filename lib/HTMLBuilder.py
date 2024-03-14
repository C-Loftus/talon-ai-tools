# Talon's imgui gui library is not accessible to screen readers.
# By using HTML we can create temporary web pages that are accessible to screen readers.

import enum
import os
import platform
import tempfile
import webbrowser


def get_style():
    # read in all the styles from a file ./styles.css
    style_path = os.path.join(os.path.dirname(__file__), "styles.css")
    with open(style_path, "r") as f:
        all_styles = f.read()

    return f"""
    <style>
    {all_styles}
    </style>
    """


class ARIARole(enum.Enum):
    MAIN = "main"
    BANNER = "banner"
    NAV = "navigation"
    FOOTER = "contentinfo"
    # TODO other roles?


class Builder:
    """
    Easily build HTML pages and add aria roles to elements
    in order to make them accessible to screen readers.
    """

    def __init__(self):
        self.elements = []
        self.doc_title = "Generated Help Page from Talon"

    def _flat_helper(self, text, tag, role=None):
        if role:
            self.elements.append(f"<{tag} role='{role.value}'>{text}</{tag}>")
        else:
            self.elements.append(f"<{tag}>{text}</{tag}>")

    def title(self, text):
        self.doc_title = text

    def h1(self, text, role=None):
        self._flat_helper(text, "h1", role)

    def h2(self, text, role=None):
        self._flat_helper(text, "h2", role)

    def h3(self, text, role=None):
        self._flat_helper(text, "h3", role)

    def p(self, text, role=None):
        self._flat_helper(text, "p", role)

    def a(self, text, href, role=None):
        self.elements.append(
            f"<a href='{href}' role='{role.value}'>{text}</a>"
            if role
            else f"<a href='{href}'>{text}</a>"
        )

    def _li(self, text):
        self._flat_helper(text, "li")

    def ul(self, *text, role=None):
        self.elements.append(f"<ul role='{role.value}'>" if role else "<ul>")

        for item in text:
            self._li(item)
        self.elements.append("</ul>")

    def ol(self, *text, role=None):
        self.elements.append(f"<ol role='{role.value}'>" if role else "<ol>")
        for item in text:
            self._li(item)
        self.elements.append("</ol>")

    def base64_img(self, img, alt="", role=None):
        self.elements.append(
            f"<img src='data:image/jpeg;base64,{img}' alt='{alt}' role='{role.value}'>"
            if role
            else f"<img src='data:image/jpeg;base64,{img}' alt='{alt}'>"
        )

    def start_table(self, headers, role=None):
        self.elements.append(f"<table role='{role.value}'>" if role else "<table>")
        self.elements.append("<thead><tr>")
        for header in headers:
            self.elements.append(f"<th>{header}</th>")
        self.elements.append("</tr></thead><tbody>")

    def add_row(self, cells):
        self.elements.append("<tr>")
        for cell in cells:
            self.elements.append(f"<td>{cell}</td>")
        self.elements.append("</tr>")

    def end_table(self):
        self.elements.append("</tbody></table>")

    def render(self):
        html_content = "\n".join(self.elements)
        full_html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{self.doc_title}</title>
            {get_style()}
        </head>
        <body>
            <div class="container">
                {html_content}
            </div>
        </body>
        </html>
        """

        # If you are using a browser through a snap package on Linux you cannot
        # open many directories so we just default to the downloads folder since that is one we can use
        if platform.system() == "Linux":
            dir = os.path.join(os.path.expanduser("~"), "Downloads")
        else:
            dir = None

        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".html", delete=False, encoding="utf-8", dir=dir
        ) as temp_file:
            temp_file.write(full_html)
            temp_file_path = temp_file.name
        webbrowser.open("file://" + os.path.abspath(temp_file_path))


# API Demo
# builder = Builder()
# builder.title("Generated Help Page from Talon")
# builder.h1("Banner Heading", role=ARIARole.BANNER)
# builder.h1("Header 1 for the page")
# builder.h2("Header 2")
# builder.h3("Smaller Header 3")
# builder.ul("Bullet 1", "Bullet number two")
# builder.p("This is a paragraph within the article", role=ARIARole.MAIN)
# builder.h2("Navigation Heading", role=ARIARole.NAV)
# builder.p("This is a paragraph within the article")
# builder.ol("First element: Hello", "Second one: World")
# builder.p("This is labeled as an aria footer within the article", role=ARIARole.FOOTER)
# builder.render()
