import sys

# We are using a separate Python interpreter to test. Talon's Python env sets up packages differently
# so we want to just manually add the library to the path.

sys.path.append(".")

from lib.pureHelpers import strip_markdown


def test_strip_markdown():
    markdown = """
    ```python
    print("hello")
    ```
    """
    assert strip_markdown(markdown) == 'print("hello")'

    markdown = """
    ```sh
    echo "hello"
    ```
    """
    assert strip_markdown(markdown) == 'echo "hello"'

    markdown = """
    ```bash
    echo "hello"
    ```
    """
    assert strip_markdown(markdown) == 'echo "hello"'

    # Unclear if this is a case we even care about
    # markdown = """
    # ```markdown
    # # Test
    # ```rust
    # println!("hello");
    # ```
    # ```
    # """
    # assert strip_markdown(markdown) == '# Test\n```rust\nprintln!("hello");```'
