# Strings definitions file

# Main config file
config_ini = "config.ini"


# Config sections

class Configs:
    class System:
        system = "system"  # Section strings
        token = "token"  # Discord token
        data = "data"  # Data directory
        dev = "dev"  # Dev ephemeral mode?
        db = "db"  # Redis host
        db_port = "db_port"  # Redis port
        db_num = "db_num"  # Redis DB number
        cache = "cache"  # Memcached host and port
        url = "url"  # Url that can be jumped from help page
        aques_api = "aques_api"  # AQTaaS (AQuesTalk as a Service) URL
        watson_api = "watson_api"  # IBM Watson API token
        watson_url = "watson_url"  # IBM Watson API url

    class Data:
        default = "default"  # Section: Default config / Config: Default policy
        prefix = "prefix"  # Command prefix
        lang = "lang"  # Language
        limit = "limit"  # Max chars
        voice = "voice"  # Default voice variant
        bots = "bots"  # If reads bots

        # Special data

        replace = "replace"

    class Lang:
        # For more details, please check english translations.
        join = "join"
        leave = "leave"
        ping = "ping"
        skip = "skip"
        prefix = "prefix"
        lang = "lang"
        limit = "limit"
        voice = "voice"
        default = "default"
        replace = "replace"
        list = "list"
        bots = "bots"
        config = "config"
        config_list = "config_list"
        config_error = "config_error"
        config_voicepack = "config_voicepack"
        warn_emoji = "warn_emoji"
        error_voice = "error_voice"
        help = "help"
        help_config = "help_config"


class Reactions:
    plusOne = "👍"
    skip = "⏩"
    raiseHand = "✋"

class Messages:
    # Console messages
    dev = "TTS bot starting in DEVELOPMENT mode! No config will be saved!"
