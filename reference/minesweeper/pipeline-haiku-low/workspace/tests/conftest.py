"""Tests run on records of their own: nothing the running app saved is read, and nothing a test creates is saved."""
import os

os.environ["APP_DATA_DIR"] = ""
