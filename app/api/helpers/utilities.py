# PLEASE PUT ALL FUNCTIONS WHICH PERFORM GENERAL FORMATTING ON ANY DATATYPE WITHOUT USING ANY
# MODULES RELATED TO THE EVENT-SYSTEM i.e FUNCTIONS RELATED TO DB MODELS, OTHER API MODULES
# OR OTHER HELPER MODULES

def dasherize(text):
    return text.replace('_', '-')


def ensure_social_link(website, link):
    """
    converts usernames of social profiles to full profile links
    if link is username, prepend website to it else return the link
    """
    if link == '' or link is None:
        return link
    if link.find('/') != -1:  # has backslash, so not a username
        return link
    else:
        return website + '/' + link
