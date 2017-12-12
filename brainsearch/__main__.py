"""
Copyright 2017 Deepgram
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from deepgram import Brain
import argparse, os, time, urllib.parse, webbrowser, time
from glob import glob
FILE_TYPES = '.mp3 .3gp .aifc .mp4 .ogg .aif .wav .amr .flac .wmv .mpg .mkv .mp2 .mov .webm .3gpp .m4a .wma .aiff .aac .3ga .links'.split()


def loadLink(brainAPI, link, previousAssets):
  urlPath = urllib.parse.urlsplit(link)[2].strip()
  basename = os.path.basename(urlPath)
  if basename in previousAssets:
    print('Reusing: {}'.format(basename))
    return previousAssets[basename][0], basename, True
  else:
    print('Loading: {}'.format(basename))
    # We want to make this async so that we can let brain process while we load more assets
    assetId = brainAPI.createAssetFromURL(link, async=True, metadata={'filename': basename})['asset_id']
    return assetId, basename, False

def loadFile(brainAPI, path, previousAssets):
  basename = os.path.basename(path)
  if basename in previousAssets:
    print('Reusing: {}'.format(basename))
    return previousAssets[basename][0], basename, True
  else:
    print('Loading: {}'.format(basename))
    with open(path, mode='rb') as data:
      # We want to make this async so that we can let brain process while we load more assets
      assetId = brainAPI.uploadAsset(data, async=True, metadata={'filename': basename})['asset_id']
      return assetId, basename, False

def main():

  parser = argparse.ArgumentParser()
  parser.add_argument('-u', '--user', help='API user id', required=True)
  parser.add_argument('-t', '--token', help='API user token', required=True)
  parser.add_argument('-s', '--server', help='URL of the API server to use.')
  parser.add_argument('-r', '--reload', help='Reload all data files to the server.', action='store_true')
  parser.add_argument('-q', '--quality', help='Minimum quality result to report.', type=float, default=.65)


  parser.add_argument('query', nargs='+', help='Phrase to search for')
  parser.add_argument('-f', '--file', help='Files to search or a link file to get link to search from.', action='append')
  parser.add_argument('-l', '--link', help='Link to search.', action='append')
  parser.add_argument('-b', '--brain-assets', help='Search all previously loaded brain assets.', action='store_true')

  args = parser.parse_args()

  #Argparse is great, but unfortunately specifying a default will append it to the list so we will check for it
  # explicitly
  fileArgs = args.file
  if fileArgs is None or len(fileArgs) == 0:
    fileArgs = ['./*']
  files = []
  #Now strip out only the files that have the right file extension
  for file in fileArgs:
    files += [file for file in glob(file) if (os.path.splitext(file)[1].lower() in FILE_TYPES)]

  if len(files) == 0 and args.link is None and not args.brain_assets:
    print('No valid inputs found.')
    exit(0)

  #Connect to Brain
  if args.server is not None:
    brainAPI = Brain(url=args.server, user_id= args.user_id, token = args.token)
  else:
    brainAPI = Brain(user_id=args.user, token=args.token)

  #To save time, lets look for any previous assets that we have loaded
  allAssets = {}
  assetIds = {}
  if not args.reload:
    for asset in brainAPI.assets:
      if ('status' not in asset or asset['status'] != 'failed') and asset['transcript_exists'] == True:
        if asset['metadata'] is not None and 'filename' in asset['metadata']:
          allAssets[asset['metadata']['filename']] = (asset['asset_id'], asset['content_url_wav'], asset['duration'])
          if args.brain_assets:
            assetIds[asset['asset_id']] = asset['metadata']['filename']
        elif args.brain_assets:
          assetIds[asset['asset_id']] = 'Asset:{}'.format(asset['asset_id'])

  #now lets load the files into brain or re-use them if they are already there
  loadingAssets = set()
  for file in files:
    if os.path.splitext(file)[1].lower() == '.links':
      with open(file) as inFile:
        for link in inFile:
          assetId, basename, reused = loadLink(brainAPI, link, allAssets)
          assetIds[assetId] = basename
          if not reused:
            loadingAssets.add(assetId)

    else:
      assetId, basename, reused = loadFile(brainAPI, file, allAssets)
      assetIds[assetId] = basename
      if not reused:
        loadingAssets.add(assetId)

  #now lets load any urls into brain or re-use them if they are already there
  if args.link is not None:
    for link in args.link:
      assetId, basename, reused = loadLink(brainAPI, link, allAssets)
      assetIds[assetId] = basename
      if not reused:
        loadingAssets.add(assetId)

  #Since we loaded asynchronously we need to wait untill all assets have finished loading to search them
  while len(loadingAssets) > 0:
    print('Waiting for assets to process...')
    for assetId in loadingAssets.copy():
      asset = brainAPI.asset(assetId)
      if asset['transcript'] is not None:
        loadingAssets.remove(assetId)
        allAssets[asset['metadata']['filename']] = (asset['asset_id'], asset['content_url_wav'], asset['duration'])
    if len(loadingAssets) > 0:
      #give it a few second until we check again
      time.sleep(2.0)


  #now search!
  startTime = time.time()
  results = brainAPI.searchAssets(' '.join(args.query), tuple(assetIds))['results']
  searchTime = time.time() - startTime

  goodResults = []
  totalDuration = 0.0
  for assetId in assetIds:
    totalDuration += allAssets[assetIds[assetId]][2]

  #and display the results
  for result in results:
    print('{} hits:'.format(assetIds[result['asset_id']]))
    for hit in result['hits']:
      if hit['quality'] >= args.quality:
        print('{}:{}'.format(hit['quality'], hit['time']))
        goodResults.append((assetIds[result['asset_id']], hit['quality'], hit['time'], allAssets[assetIds[result['asset_id']]][1]))

  # Now lets generate a quick results page and show them to the user
  with open('results.html', mode='w') as resultsFile:
    resultsFile.write('<html><head><title>Search Results</title></head><body>')
    resultsFile.write('<b>Search query:</b> {}<br>'.format(' '.join(args.query)))
    resultsFile.write('<b>Seconds of audio searched:</b> {:0.2f}<br>'.format(totalDuration))
    resultsFile.write('<b>Search completed in {:0.2f} seconds. A {:0.2f}% speedup!</b><br>'.format(searchTime, 100*(totalDuration/searchTime)))
    if len(goodResults) > 0:
      resultsFile.write('<b>Results:</b><br>')
      for idx, (basename, quality, hitTime, mp3URL) in enumerate(goodResults):
        resultsFile.write('<p><b>{}</b>: At {:0.2f} with quality {:0.2f}</br>'.format(basename, hitTime, quality))
        resultsFile.write('<audio id="audio{}" preload="none" src="{}" controls/></p>'.format(idx, mp3URL))
        resultsFile.write('<script>document.getElementById("audio{}").currentTime={};</script>'.format(idx, hitTime - 1))
    else:
      resultsFile.write('<b>No results found.</b>')
    resultsFile.write('</body></html>')

  webbrowser.open('file://' + os.path.abspath('results.html'))

if __name__ == '__main__':
  main()


