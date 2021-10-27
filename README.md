# Kotone

Discord TTS bot mainly forcused on Japanese: finally opensourced. yay!

## EOL

Due to archive of the discord.py library and instable behavior of the bot: We'll stop support of the Kotone at end of the month(October 2021).

## Japanese

### インストールヒント

- memcachedを入れて起動してください
- redisを入れて起動してください
- mecabをインストールしてください
- pipでrequirements.txtを使って依存関係を解決してください(venvの使用を推奨)
- english_to_kana.pyを開いてコメントの指示に従ってください
- config.iniを開いてtokenを設定してください
- DiscordBotの設定で、Server Members Intentを有効化してください

#### GCPを使用する場合
- GCPのプロジェクトでText-to-Speech APIを有効化します
- Wavenet音声(高品質で高価)を使用する場合、config.iniのgcp_voicetypeを、Wavenetに変更します

Google Cloud SDKを使用している、またはCompute Cloud上で実行するなど、認証情報が自動取得可能なら準備完了です

それ以外の場合
- 認証情報をjsonファイルで入手します
- config.iniのgcp_credentials_path、または環境変数GOOGLE_APPLICATION_CREDENTIALSに、認証用のjsonへのパスを設定します

認証用jsonの入手方法の参考ページ  
https://cloud.google.com/docs/authentication/production?hl=ja#manually

#### mecabインストール
お使いのOSのパッケージマネージャでインストールすることが推奨されます  
Debian系  
`# apt install mecab libmecab-dev mecab-ipadic`

Arch Linux  
mecab(AUR),mecab-ipadic(AUR)

手動でのMecabインストール方法  
http://taku910.github.io/mecab/#download
