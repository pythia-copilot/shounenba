# Shounenba 正念場

Shounenba leverages the power of OpenAI's ChatGPT to provide instant, reliable answers to help you throughout your interview process.

## Introduction

<img src="/1.png" alt="Tkinter Interface" width=50%/>

Shounenba is a Python Tkinter-based application designed to transform the remote interview experience by providing real-time AI assistance. By harnessing the capabilities of OpenAI's ChatGPT and Deepgram's advanced speech recognition technology, Shounenba aids users in generating relevant questions, offering instant answers to fact-based inquiries, and suggesting insightful follow-up questions. This tool aims to streamline the interview process for both interviewers and candidates, ensuring a smooth and effective exchange of information and enhancing overall interview performance.

## See Also

| Service  | Description |
| ------------- | ------------- |
| Pythia  | Coming Soon  |
| 皮西娅  | 敬请期待  |

## Usage

## Prerequisites

Before you begin, ensure you have the following installed on your system:

Python <br />
git <br />
pip (Python package installer) <br />
<br />
And of course, an API key from [Openai](https://platform.openai.com/) and [Deepgram](https://deepgram.com).

## Installation

## Clone or download the Repository:

```bash
git clone https://github.com/pythia-copilot/shounenba.git
```

## Install Dependencies:

```bash
pip install -r requirements.txt
```

## Create a Virtual Environment (optional but recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```
Or manually setup in process.py line 11 and reveive.py line 219.

## Configuration

Setting Up BlackHole for Mac: <br />
<br />
visit [Blackhole](https://github.com/ExistentialAudio/BlackHole) and install. <br />
Set Up Multi-Output Device: <br />
Right-click your new [Multi-Output Device](https://github.com/ExistentialAudio/BlackHole/wiki/Multi-Output-Device) and select 'Use This Device For Sound Output'.
<br />
<br />

Setting Up VB-CABLE for Windows: <br />
visit [VB-Cable](https://vb-audio.com/Cable/index.htm) or other virtual audio cable and install. <br />
Configure VB-CABLE  <br />
Notice Windows users may need to configure receive.py as well. <br />

## Run the app

```bash
cd shounenba
python main.py
```

## Interact with Shounenba
Reset Transcript: reset transcript buffer <br />
Send: Send transcript buffer, and reset it

## Disclaimer

Shounenba is a satirical art project and is not intended for use in real-world settings. It may generate incorrect or inappropriate solutions. Users should exercise caution and take responsibility for the information provided by the app.
