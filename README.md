[![GibsonAI](https://s3.us-east-1.amazonaws.com/images.memorilabs.ai/banner.png)](https://memorilabs.ai/)

# memori

<p align="center">
  <strong>An open-source SQL-Native memory engine for AI</strong>
</p>

<p align="center">
  <i>From Postgres to MySQL, Memori plugs into the SQL databases you already use. Simple setup, infinite scale without new infrastructure.</i>
</p>

<p align="center">
  <a href="https://memorilabs.ai/">Learn more</a>
  ·
  <a href="https://www.gibsonai.com/discord">Join Discord</a>
</p>

<p align="center">
  <a href="https://badge.fury.io/py/memorisdk">
    <img src="https://badge.fury.io/py/memori.svg" alt="PyPI version">
  </a>
  <a href="https://pepy.tech/projects/memorisdk">
    <img src="https://static.pepy.tech/badge/memorisdk" alt="Downloads">
  </a>
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  </a>
</p>

---

# Getting Started

Install Memori:

    pip install memori

# Example with OpenAI

    from openai import OpenAI
    from memori import Memori

    client = OpenAI(...)
    mem = Memori().openai.register(client)

# Attribution

    mem.attribution(parent_id="12345", process_id="my-ai-bot")

# Session Management

    mem.new_session()

    or

    session_id = mem.config.session_id

    ...

    mem.set_session(session_id)
