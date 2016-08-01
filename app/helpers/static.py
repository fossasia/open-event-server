# -*- coding: utf-8 -*-

##
# Module for helper static variables
##

# Event Licences

EVENT_LICENCES = {
    # Licence Name : ( Long Name, Description, Licence URL, Licence Logo, Licence Compact Logo )
    'All rights reserved': (
        'All rights reserved',
        u'The copyright holder reserves, or holds for their own use, all the rights provided by copyright law under one specific copyright treaty.',
        'https://en.wikipedia.org/wiki/All_rights_reserved',
        '',
        ''),
    'Attribution': (
        'Creative Commons Attribution 4.0 International License',
        u'This license lets others distribute, remix, tweak, and build upon the work, even commercially, as long as they credit the copyright holder for the original creation.',
        'https://creativecommons.org/licenses/by/4.0',
        'https://licensebuttons.net/l/by/3.0/88x31.png',
        'https://licensebuttons.net/l/by/3.0/80x15.png'),
    'Attribution-ShareAlike': (
        'Creative Commons Attribution-ShareAlike 4.0 International License',
        u'This license lets others remix, tweak, and build upon the work even for commercial purposes, as long as they credit the copyright holder and license their new creations under the identical terms.',
        'https://creativecommons.org/licenses/by-sa/4.0',
        'https://licensebuttons.net/l/by-sa/3.0/88x31.png',
        'https://licensebuttons.net/l/by-sa/3.0/80x15.png'),
    'Attribution-NoDerivs': (
        'Creative Commons Attribution-NoDerivs 4.0 International License',
        u'This license allows for redistribution, commercial and non-commercial, as long as it is passed along unchanged and in whole, with credit to the copyright holder.',
        'https://creativecommons.org/licenses/by-nd/4.0',
        'https://licensebuttons.net/l/by-nd/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nd/3.0/80x15.png'),
    'Attribution-NonCommercial': (
        'Creative Commons Attribution-NonCommercial 4.0 International License',
        u'This license lets others remix, tweak, and build upon the work non-commercially, and although their new works must also acknowledge the copyright holder and be non-commercial, they don’t have to license their derivative works on the same terms.',
        'https://creativecommons.org/licenses/by-nc/4.0',
        'https://licensebuttons.net/l/by-nc/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nc/3.0/80x15.png'),
    'Attribution-NonCommercial-NoDerivs': (
        'Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License',
        u'This license only allows others to download the work and share them with others as long as they credit the copyright holder, but they can’t change them in any way or use them commercially.',
        'https://creativecommons.org/licenses/by-nc-nd/4.0',
        'https://licensebuttons.net/l/by-nc-nd/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nc-nd/3.0/80x15.png'),
    'Attribution-NonCommercial-ShareAlike': (
        'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License',
        u'This license lets others remix, tweak, and build upon the work non-commercially, as long as they credit the copyright holder and license their new creations under the identical terms.',
        'https://creativecommons.org/licenses/by-nc-sa/4.0',
        'https://licensebuttons.net/l/by-nc-sa/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nc-sa/3.0/80x15.png'),
    'Public Domain Dedication (CC0)': (
        'Creative Commons Public Domain Dedication (CC0)',
        u'The copyright holder waives his interest in his work and places the work as completely as possible in the public domain so others may freely exploit and use the work without restriction under copyright or database law.',
        'https://creativecommons.org/publicdomain/zero/1.0/',
        'http://i.creativecommons.org/p/zero/1.0/88x31.png',
        'http://i.creativecommons.org/p/zero/1.0/80x15.png'),
    'Public Domain Work': (
        'Creative Commons Public Domain Work',
        u'This license enables works that are no longer restricted by copyright to be marked as such in a standard and simple way, making them easily discoverable and available to others.',
        'https://creativecommons.org/publicdomain/mark/1.0/',
        'https://licensebuttons.net/p/mark/1.0/88x31.png',
        'https://licensebuttons.net/p/mark/1.0/80x15.png')
}

# Event Topics with sub topics

EVENT_TOPICS = {
    'Auto, Boat & Air': ['Air', 'Auto', 'Boat', 'Motorcycle/ATV', 'Other'],
    'Business & Professional': [
        'Career', 'Design', 'Educators', 'Environment &amp; Sustainability',
        'Finance', 'Media', 'Non Profit &amp; NGOs', 'Other', 'Real Estate',
        'Sales &amp; Marketing', 'Startups &amp; Small Business'
    ],
    'Charity & Causes': [
        'Animal Welfare', 'Disaster Relief', 'Education',
        'Environment', 'Healthcare', 'Human Rights',
        'International Aid', 'Other', 'Poverty'
    ],
    'Community & Culture': [
        'City/Town', 'County', 'Heritage', 'LGBT', 'Language',
        'Medieval', 'Nationality', 'Other', 'Renaissance', 'State'
    ],
    'Family & Education': [
        'Alumni', 'Baby', 'Children &amp; Youth', 'Education', 'Other',
        'Parenting', 'Parents Association', 'Reunion'
    ],
    'Fashion & Beauty': [
        'Accessories', 'Beauty', 'Bridal', 'Fashion', 'Other'
    ],
    'Film, Media & Entertainment': [
        'Adult', 'Anime', 'Comedy', 'Comics', 'Film', 'Gaming', 'Other', 'TV'
    ],
    'Food & Drink': ["Beer", "Food", "Other", "Spirits", "Wine"],
    'Government & Politics': [
        "County/Municipal Government", "Democratic Party", "Federal Government",
        "Non-partisan", "Other", "Other Party", "Republican Party",
        "State Government"
    ],
    'Health & Wellness': [
        "Medical", "Mental health", "Other", "Personal health", "Spa", "Yoga"
    ],
    'Hobbies & Special Interest': [
        "Adult", "Anime/Comics", "Books", "DIY", "Drawing & Painting", "Gaming",
        "Knitting", "Other", "Photography"
    ],
    'Home & Lifestyle': ["Dating", "Home & Garden", "Other", "Pets & Animals"],
    'Music': [
        "Alternative", "Blues & Jazz", "Classical", "Country", "Cultural",
        "EDM / Electronic", "Folk", "Hip Hop / Rap", "Indie", "Latin", "Metal",
        "Opera", "Other", "Pop", "R&B", "Reggae", "Religious/Spiritual", "Rock",
        "Top 40"
    ],
    'Other': [],
    'Performing & Visual Arts': [
        "Ballet", "Comedy", "Craft", "Dance", "Fine Art", "Literary Arts",
        "Musical", "Opera", "Orchestra", "Other", "Theatre"
    ],
    'Religion & Spirituality': [
        "Buddhism", "Christianity", "Eastern Religion", "Islam", "Judaism",
        "Mormonism", "Mysticism and Occult", "New Age", "Other", "Sikhism"
    ],
    'Science & Technology': [
        "Biotech", "High Tech", "Medicine", "Mobile", "Other", "Robotics",
        "Science", "Social Media"
    ],
    'Seasonal & Holiday': [
        "Channukah", "Christmas", "Easter", "Fall events", "Halloween/Haunt",
        "Independence Day", "New Years Eve", "Other", "St Patricks Day",
        "Thanksgiving"
    ],
    'Sports & Fitness': [
        "Baseball", "Basketball", "Cycling", "Exercise", "Fighting & Martial Arts",
        "Football", "Golf", "Hockey", "Motorsports", "Mountain Biking",
        "Obstacles", "Other", "Rugby", "Running", "Snow Sports", "Soccer",
        "Swimming & Water Sports", "Tennis", "Volleyball", "Walking", "Yoga"
    ],
    'Travel & Outdoor': [
        "Canoeing", "Climbing", "Hiking", "Kayaking", "Other", "Rafting", "Travel"
    ]
}

# Event Images with Event Topics

DEFAULT_EVENT_IMAGES = {
    'Auto, Boat & Air': '',
    'Business & Professional': '',
    'Charity & Causes': '',
    'Community & Culture': '',
    'Family & Education': '',
    'Fashion & Beauty': '',
    'Film, Media & Entertainment': '',
    'Food & Drink': '',
    'Government & Politics': '',
    'Health & Wellness': '',
    'Hobbies & Special Interest': '',
    'Home & Lifestyle': '',
    'Music': '',
    'Other': '',
    'Performing & Visual Arts': '',
    'Religion & Spirituality': '',
    'Science & Technology': '',
    'Seasonal & Holiday': '',
    'Sports & Fitness': '',
    'Travel & Outdoor': ''
}
