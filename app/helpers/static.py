# -*- coding: utf-8 -*-

##
# Module for helper static variables
##

# Event Licences

EVENT_LICENCES = {
    # Licence Name : ( Long Name, Description, Licence URL, Licence Logo, Licence Compact Logo )
    'All rights reserved': (
        'All rights reserved',
        u'The copyright holder reserves, or holds for their own use, all the rights provided by copyright law under '
        u'one specific copyright treaty.',
        'https://en.wikipedia.org/wiki/All_rights_reserved',
        '',
        ''),
    'Attribution': (
        'Creative Commons Attribution 4.0 International License',
        u'This license lets others distribute, remix, tweak, and build upon the work, even commercially, as long as '
        u'they credit the copyright holder for the original creation.',
        'https://creativecommons.org/licenses/by/4.0',
        'https://licensebuttons.net/l/by/3.0/88x31.png',
        'https://licensebuttons.net/l/by/3.0/80x15.png'),
    'Attribution-ShareAlike': (
        'Creative Commons Attribution-ShareAlike 4.0 International License',
        u'This license lets others remix, tweak, and build upon the work even for commercial purposes, as long as '
        u'they credit the copyright holder and license their new creations under the identical terms.',
        'https://creativecommons.org/licenses/by-sa/4.0',
        'https://licensebuttons.net/l/by-sa/3.0/88x31.png',
        'https://licensebuttons.net/l/by-sa/3.0/80x15.png'),
    'Attribution-NoDerivs': (
        'Creative Commons Attribution-NoDerivs 4.0 International License',
        u'This license allows for redistribution, commercial and non-commercial, as long as it is passed along '
        u'unchanged and in whole, with credit to the copyright holder.',
        'https://creativecommons.org/licenses/by-nd/4.0',
        'https://licensebuttons.net/l/by-nd/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nd/3.0/80x15.png'),
    'Attribution-NonCommercial': (
        'Creative Commons Attribution-NonCommercial 4.0 International License',
        u'This license lets others remix, tweak, and build upon the work non-commercially, and although their new '
        u'works must also acknowledge the copyright holder and be non-commercial, they don’t have to license their '
        u'derivative works on the same terms.',
        'https://creativecommons.org/licenses/by-nc/4.0',
        'https://licensebuttons.net/l/by-nc/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nc/3.0/80x15.png'),
    'Attribution-NonCommercial-NoDerivs': (
        'Creative Commons Attribution-NonCommercial-NoDerivs 4.0 International License',
        u'This license only allows others to download the work and share them with others as long as they credit the '
        u'copyright holder, but they can’t change them in any way or use them commercially.',
        'https://creativecommons.org/licenses/by-nc-nd/4.0',
        'https://licensebuttons.net/l/by-nc-nd/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nc-nd/3.0/80x15.png'),
    'Attribution-NonCommercial-ShareAlike': (
        'Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License',
        u'This license lets others remix, tweak, and build upon the work non-commercially, as long as they credit the '
        u'copyright holder and license their new creations under the identical terms.',
        'https://creativecommons.org/licenses/by-nc-sa/4.0',
        'https://licensebuttons.net/l/by-nc-sa/3.0/88x31.png',
        'https://licensebuttons.net/l/by-nc-sa/3.0/80x15.png'),
    'Public Domain Dedication (CC0)': (
        'Creative Commons Public Domain Dedication (CC0)',
        u'The copyright holder waives his interest in his work and places the work as completely as possible in the '
        u'public domain so others may freely exploit and use the work without restriction under copyright or database '
        u'law.',
        'https://creativecommons.org/publicdomain/zero/1.0/',
        'http://i.creativecommons.org/p/zero/1.0/88x31.png',
        'http://i.creativecommons.org/p/zero/1.0/80x15.png'),
    'Public Domain Work': (
        'Creative Commons Public Domain Work',
        u'This license enables works that are no longer restricted by copyright to be marked as such in a standard '
        u'and simple way, making them easily discoverable and available to others.',
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
    'Other': ["Avatar"],
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
PAYMENT_COUNTRIES = {
    'United States',
    'Argentina',
    'Australia',
    'Austria',
    'Belgium',
    'Brazil',
    'Canada',
    'Cyprus',
    'Czech Republic',
    'Denmark',
    'Estonia',
    'Finland',
    'France',
    'Germany',
    'Greece',
    'Hong Kong',
    'Hungary',
    'Ireland',
    'Israel',
    'Italy',
    'Japan',
    'Latvia',
    'Lithuania',
    'Luxemborg',
    'Malaysia',
    'Malta',
    'Mexico',
    'Netherlands',
    'New Zealand',
    'Norway',
    'Philippines',
    'Poland',
    'Portugal',
    'Singapore',
    'Slovakia',
    'Slovenia',
    'Spain',
    'Sweden',
    'Switzerland',
    'Taiwan',
    'United Kingdom',
}

# (currency_code,available_on_paypal,available_on_stripe)
PAYMENT_CURRENCIES = {
    ('AUD', True, True),
    ('BRL', True, True),
    ('CAD', True, True),
    ('CHF', True, True),
    ('CZK', True, True),
    ('DKK', True, True),
    ('EUR', True, True),
    ('GBP', True, True),
    ('HKD', True, True),
    ('HUF', True, True),
    ('ILS', True, True),
    ('INR', False, True),
    ('JPY', True, True),
    ('MXN', True, True),
    ('MYR', True, True),
    ('NOK', True, True),
    ('NZD', True, True),
    ('PHP', True, True),
    ('PLN', True, True),
    ('RUB', True, True),
    ('SEK', True, True),
    ('SGD', True, True),
    ('THB', True, True),
    ('TWD', True, True),
    ('USD', True, True),
}

# Event Images with Event Topics and Subtopics

DEFAULT_EVENT_IMAGES = {
    'Hiking': 'Hiking.jpg',
    'Republican Party': 'RepublicanParty.jpg',
    'Literary Arts': 'LiteraryArts.jpg',
    'Cycling': 'Cycling.jpg',
    'Travel & Outdoor': 'Travel&Outdoor.jpg',
    'Religious/Spiritual': 'Religious/Spiritual.jpg',
    'EDM / Electronic': 'EDM/Electronic.jpg',
    'Social Media': 'SocialMedia.jpg',
    'Fine Art': 'FineArt.jpg',
    'Performing & Visual Arts': 'Performing&VisualArts.jpg',
    'Environment': 'Environment.jpg',
    'Pets & Animals': 'Pets&Animals.jpg',
    'Buddhism': 'Buddhism.jpg',
    'Environment & Sustainability': 'Environment&Sustainability.jpg',
    'Music': 'Music.jpg',
    'Mountain Biking': 'MountainBiking.jpg',
    'Mysticism and Occult': 'MysticismandOccult.jpg',
    'Medicine': 'Medicine.jpg',
    'Yoga': 'Yoga.jpg',
    'Comedy': 'Comedy.jpg',
    'Non Profit & NGOs': 'NonProfit&NGOs.jpg',
    'Family & Education': 'Family&Education.jpg',
    'Disaster Relief': 'DisasterRelief.jpg',
    'Blues & Jazz': 'Blues&Jazz.jpg',
    'Gaming': 'Gaming.jpg',
    'Knitting': 'Knitting.jpg',
    'Finance': 'Finance.jpg',
    'Beauty': 'Beauty.jpg',
    'Parenting': 'Parenting.jpg',
    'Parents Association': 'ParentsAssociation.jpg',
    'Photography': 'Photography.jpg',
    'New Years Eve': 'NewYearsEve.jpg',
    'Cultural': 'Cultural.jpg',
    'Musical': 'Musical.jpg',
    'Motorsports': 'Motorsports.jpg',
    'Craft': 'Craft.jpg',
    'Baseball': 'Baseball.jpg',
    'Adult': 'Adult.jpg',
    'International Aid': 'InternationalAid.jpg',
    'Religion & Spirituality': 'Religion&Spirituality.jpg',
    'Fall events': 'Fallevents.jpg',
    'Mobile': 'Mobile.jpg',
    'Tennis': 'Tennis.jpg',
    'Judaism': 'Judaism.jpg',
    'Running': 'Running.jpg',
    'Language': 'Language.jpg',
    'Biotech': 'Biotech.jpg',
    'Career': 'Career.jpg',
    'Eastern Religion': 'EasternReligion.jpg',
    'Motorcycle/ATV': 'Motorcycle/ATV.jpg',
    'Alumni': 'Alumni.jpg',
    'Thanksgiving': 'Thanksgiving.jpg',
    'Volleyball': 'Volleyball.jpg',
    'Air': 'Air.jpg',
    'Mormonism': 'Mormonism.jpg',
    'Auto, Boat & Air': 'Auto,Boat&Air.jpg',
    'Beer': 'Beer.jpg',
    'Healthcare': 'Healthcare.jpg',
    'R&B': 'R&B.jpg',
    'Wine': 'Wine.jpg',
    'Film, Media & Entertainment': 'Film,Media&Entertainment.jpg',
    'Food & Drink': 'Food&Drink.jpg',
    'Fashion': 'Fashion.jpg',
    'Golf': 'Golf.jpg',
    'Anime/Comics': 'Anime/Comics.jpg',
    'Classical': 'Classical.jpg',
    'Educators': 'Educators.jpg',
    'Indie': 'Indie.jpg',
    'High Tech': 'HighTech.jpg',
    'Robotics': 'Robotics.jpg',
    'Accessories': 'Accessories.jpg',
    'Animal Welfare': 'AnimalWelfare.jpg',
    'County': 'County.jpg',
    'Climbing': 'Climbing.jpg',
    'Books': 'Books.jpg',
    'Reunion': 'Reunion.jpg',
    'Top 40': 'Top40.jpg',
    'Education': 'Education.jpg',
    'Reggae': 'Reggae.jpg',
    'Boat': 'Boat.jpg',
    'Independence Day': 'IndependenceDay.jpg',
    'Human Rights': 'HumanRights.jpg',
    'Canoeing': 'Canoeing.jpg',
    'Ballet': 'Ballet.jpg',
    'Basketball': 'Basketball.jpg',
    'Spirits': 'Spirits.jpg',
    'Home & Garden': 'Home&Garden.jpg',
    'Non-partisan': 'Non-partisan.jpg',
    'Media': 'Media.jpg',
    'Science & Technology': 'Science&Technology.jpg',
    'Fighting & Martial Arts': 'Fighting&MartialArts.jpg',
    'Orchestra': 'Orchestra.jpg',
    'Christianity': 'Christianity.jpg',
    'State': 'State.jpg',
    'Other': 'Other.jpg',
    'DIY': 'DIY.jpg',
    'Heritage': 'Heritage.jpg',
    'Business & Professional': 'Business&Professional.jpg',
    'Soccer': 'Soccer.jpg',
    'Easter': 'Easter.jpg',
    'Bridal': 'Bridal.jpg',
    'County/Municipal Government': 'County/MunicipalGovernment.jpg',
    'Hobbies & Special Interest': 'Hobbies&SpecialInterest.jpg',
    'Dating': 'Dating.jpg',
    'Government & Politics': 'Government&Politics.jpg',
    'Theatre': 'Theatre.jpg',
    'Halloween/Haunt': 'Halloween/Haunt.jpg',
    'TV': 'TV.jpg',
    'Auto': 'Auto.jpg',
    'Snow Sports': 'SnowSports.jpg',
    'Health & Wellness': 'Health&Wellness.jpg',
    'Christmas': 'Christmas.jpg',
    'Renaissance': 'Renaissance.jpg',
    'Federal Government': 'FederalGovernment.jpg',
    'Poverty': 'Poverty.jpg',
    'Sikhism': 'Sikhism.jpg',
    'Seasonal & Holiday': 'Seasonal&Holiday.jpg',
    'Science': 'Science.jpg',
    'Baby': 'Baby.jpg',
    'Nationality': 'Nationality.jpg',
    'Pop': 'Pop.jpg',
    'Other Party': 'OtherParty.jpg',
    'Opera': 'Opera.jpg',
    'Football': 'Football.jpg',
    'Kayaking': 'Kayaking.jpg',
    'Rugby': 'Rugby.jpg',
    'Swimming & Water Sports': 'Swimming&WaterSports.jpg',
    'Charity & Causes': 'Charity&Causes.jpg',
    'Hip Hop / Rap': 'HipHop/Rap.jpg',
    'Comics': 'Comics.jpg',
    'Country': 'Country.jpg',
    'Sales & Marketing': 'Sales&Marketing.jpg',
    'Obstacles': 'Obstacles.jpg',
    'Metal': 'Metal.jpg',
    'LGBT': 'LGBT.jpg',
    'Startups & Small Business': 'Startups&SmallBusiness.jpg',
    'Anime': 'Anime.jpg',
    'Rock': 'Rock.jpg',
    'Walking': 'Walking.jpg',
    'Sports & Fitness': 'Sports&Fitness.jpg',
    'Rafting': 'Rafting.jpg',
    'Alternative': 'Alternative.jpg',
    'Medieval': 'Medieval.jpg',
    'Exercise': 'Exercise.jpg',
    'Fashion & Beauty': 'Fashion&Beauty.jpg',
    'State Government': 'StateGovernment.jpg',
    'Latin': 'Latin.jpg',
    'Travel': 'Travel.jpg',
    'Dance': 'Dance.jpg',
    'Democratic Party': 'DemocraticParty.jpg',
    'Avatar': 'avatar.png',
    'City/Town': 'City/Town.jpg',
    'Home & Lifestyle': 'Home&Lifestyle.jpg',
    'New Age': 'NewAge.jpg',
    'Food': 'Food.jpg',
    'Children & Youth': 'Children&Youth.jpg',
    'Design': 'Design.jpg',
    'Folk': 'Folk.jpg',
    'Hockey': 'Hockey.jpg',
    'Real Estate': 'RealEstate.jpg',
    'Drawing & Painting': 'Drawing&Painting.jpg',
    'St Patricks Day': 'StPatricksDay.jpg',
    'Community & Culture': 'Community&Culture.jpg',
    'Channukah': 'Channukah.jpg',
    'Film': 'Film.jpg',
    'Islam': 'Islam.jpg',
    'Medical': 'Medical.jpg',
    'Mental Health': 'MentalHealth.jpg',
    'Personal Health': 'PersonalHealth.jpg',
    'Spa': 'Spa.jpg',
}
