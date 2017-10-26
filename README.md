# brain-search-example
Example application that searches audio files in a directory

# Installation:
    git clone https://github.com/deepgram/brain-search-example.git
    cd deepgram-brain-search
    python setup.py install

# Obtaining an API User ID and Token
Obtaining an API User ID and token is easy. Just sign up for an account at www.deepgram.com, login and go to the API page.

![Alt text](apipage.png?raw=true "API Page")
# Usage
By default all audio sources in the current directory will be searched so the simplest usage is:

brainsearch -u <user_id> -t \<token> search phrase

#### brainsearch takes the following parameters:
    -u --user: API user id. Obtain yours by logging in to Deepgram.com and clicking API
    -t --token: API token. Obtain yours by logging in to Deepgram.com and clicking API
    query: phrase to search the audio for
    -f --file: (optional, default ./*) Location of file or files to search. Can be specified multiple times. -f ./* -f ./testdata/*
    -s --server: (optional, defalt https://brain.deepgram.com) URL of the Brain API server to use.
    -q --quality: (optional, default .6) Minimum quality result to show.
    -r --reload: (optional flag) Do not use assets already loaded on the server. Reload all specified files.


# Try these

#### Search some local files
In the repository are two chapters from public domain audio clips of Alice's Adventures in Wonderland. More great clips cn be found on LibriVox.com. Try the following to quickly get you started!

    brainsearch -u <user_id> -t <token> -f ./testdata/*.mp3 oh my ears and whiskers
    brainsearch -u <user_id> -t <token> -f ./testdata/*.mp3 off with her head

#### Search collections of files
Several link collections are in the testdata directory. Try searching some of Shakespeare's sonnets!

    brainsearch -u <user_id> -t <token> -f ./testdata/shakespeare.links within thine own deep sunken eyes

Or find some wisdom and humor from Twain

    brainsearch -u <user_id> -t <token> -f ./testdata/twain.links Persons attempting to find a motive in this narrative

#### Search everything!

    brainsearch -u <user_id> -t <token> -f ./testdata/* mother

# What next?
That is up to you. Give it a try! Most popular audio and video formats are supported. If you build something cool with search or the API, let us know!

https://www.deepgram.com/contact/

