# BilliFamilix

## Prerequisites

This application has been developed with Python 3.12.0.

You need to have an `.env` file in the root project directory with the following variables:

`AWS_ACCESS_KEY_ID=<YOUR AWS ACCESES KEY ID>`
`AWS_SECRET_ACCESS_KEY=<YOUR AWS SECRET ACCESES KEY>`

The role associated with these credentials needs to have full access to AWS Bedrock.


### Running the Application

First clone the code base and set up a Python virtual environment:

1. Clone the code an ``cd`` in the directory
2. Create a Python3 Virtual environment, e.g. ``python3 -m venv venv``
3. Activate the created environment: ``source venv/bin/activate`` 
3. bis For Windows ``.\venv\Scripts\activate``
4. Install the requirements via ``pip install -r requirements.txt``
python
Afterwards, you can run the Gradio application simply by:

```
python app.py
```


## How to contribute

1) Create a **temporary branch** with an appropriate name where you'll be making the code changes.
2) Add **docstrings and comments** to your code to provide enough explanations for other developers and reviewers. 
3) Although unit testing is not part of this repository yet, it's your responsibility to test the developed functionality properly (i.e. checking that all application functionalities have been preserved).
4) Create a pull request with a description of what has been done. 
5) The temporary branch will be deleted after a successful merge with development/master branch.



