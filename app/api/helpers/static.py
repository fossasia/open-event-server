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
    'Other': ["Avatar", "Logo"],
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
PAYMENT_COUNTRIES = [
    'US',
    'AL',
    'AR',
    'AU',
    'AT',
    'BE',
    'BR',
    'CA',
    'CY',
    'CZ',
    'DK',
    'EE',
    'FI',
    'FR',
    'DE',
    'GR',
    'HK',
    'HU',
    'IE',
    'IL',
    'IT',
    'JP',
    'LV',
    'LT',
    'LU',
    'MY',
    'MT',
    'MX',
    'NL',
    'NZ',
    'NO',
    'PH',
    'PK',
    'PO',
    'SG',
    'SK',
    'SI',
    'ES',
    'SE',
    'CH',
    'TW',
    'GB',
]

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
    'Accessories': 'Accessories.jpg',
    'Adult': 'Adult.jpg',
    'Air': 'Air.jpg',
    'Alternative': 'Alternative.jpg',
    'Alumni': 'Alumni.jpg',
    'Animal Welfare': 'AnimalWelfare.jpg',
    'Anime': 'Anime.jpg',
    'Anime/Comics': 'Anime.jpg',
    'Auto': 'Auto.jpg',
    'Auto, Boat & Air': 'AutoBoatAir.jpg',
    'Avatar': 'avatar.png',
    'Baby': 'Baby.jpg',
    'Ballet': 'Ballet.jpg',
    'Baseball': 'Baseball.jpg',
    'Basketball': 'Basketball.jpg',
    'Beauty': 'Beauty.jpg',
    'Beer': 'Beer.jpg',
    'Biotech': 'Biotech.jpg',
    'Blues & Jazz': 'BluesJazz.jpg',
    'Boat': 'Boat.jpg',
    'Books': 'Books.jpg',
    'Bridal': 'Bridal.jpg',
    'Buddhism': 'Buddhism.jpg',
    'Business & Professional': 'BusinessProfessional.jpg',
    'Canoeing': 'Canoeing.jpg',
    'Career': 'Career.jpg',
    'Channukah': 'Channukah.jpg',
    'Charity & Causes': 'CharityCauses.jpg',
    'Children & Youth': 'ChildrenYouth.jpg',
    'Christianity': 'Christianity.jpg',
    'Christmas': 'Christmas.jpg',
    'City/Town': 'CityTown.jpg',
    'Classical': 'Classical.jpg',
    'Climbing': 'Climbing.jpg',
    'Comedy': 'Comedy.jpg',
    'Comics': 'Comics.jpg',
    'Community & Culture': 'CommunityCulture.jpg',
    'Country': 'Country.jpg',
    'County': 'County.jpg',
    'County/Municipal Government': 'CountyMunicipalGovernment.jpg',
    'Craft': 'Craft.jpg',
    'Cultural': 'Cultural.jpg',
    'Cycling': 'Cycling.jpg',
    'DIY': 'DIY.jpg',
    'Dance': 'Dance.jpg',
    'Dating': 'Dating.jpg',
    'Democratic Party': 'DemocraticParty.jpg',
    'Design': 'Design.jpg',
    'Disaster Relief': 'DisasterRelief.jpg',
    'Drawing & Painting': 'DrawingPainting.jpg',
    'EDM / Electronic': 'EDMElectronic.jpg',
    'Easter': 'Easter.jpg',
    'Eastern Religion': 'EasternReligion.jpg',
    'Education': 'Education.jpg',
    'Educators': 'Educators.jpg',
    'Environment & Sustainability': 'EnvironmentSustainability.jpg',
    'Environment': 'Environment.jpg',
    'Exercise': 'Exercise.jpg',
    'Fall events': 'Fallevents.jpg',
    'Family & Education': 'FamilyEducation.jpg',
    'Fashion & Beauty': 'FashionBeauty.jpg',
    'Fashion': 'Fashion.jpg',
    'Federal Government': 'FederalGovernment.jpg',
    'Fighting & Martial Arts': 'FightingMartialArts.jpg',
    'Film': 'Film.jpg',
    'Film, Media & Entertainment': 'FilmMediaEntertainment.jpg',
    'Finance': 'Finance.jpg',
    'Fine Art': 'FineArt.jpg',
    'Folk': 'Folk.jpg',
    'Food & Drink': 'FoodDrink.jpg',
    'Food': 'Food.jpg',
    'Football': 'Football.jpg',
    'Gaming': 'Gaming.jpg',
    'Golf': 'Golf.jpg',
    'Government & Politics': 'GovernmentPolitics.jpg',
    'Halloween/Haunt': 'HalloweenHaunt.jpg',
    'Health & Wellness': 'HealthWellness.jpg',
    'Healthcare': 'Healthcare.jpg',
    'Heritage': 'Heritage.jpg',
    'High Tech': 'HighTech.jpg',
    'Hiking': 'Hiking.jpg',
    'Hip Hop / Rap': 'HipHopRap.jpg',
    'Hobbies & Special Interest': 'HobbiesSpecialInterest.jpg',
    'Hockey': 'Hockey.jpg',
    'Home & Garden': 'Home&Garden.jpg',
    'Home & Lifestyle': 'Home&Lifestyle.jpg',
    'Human Rights': 'HumanRights.jpg',
    'Independence Day': 'IndependenceDay.jpg',
    'Indie': 'Indie.jpg',
    'International Aid': 'InternationalAid.jpg',
    'Islam': 'Islam.jpg',
    'Judaism': 'Judaism.jpg',
    'Kayaking': 'Kayaking.jpg',
    'Knitting': 'Knitting.jpg',
    'LGBT': 'LGBT.jpg',
    'Language': 'Language.jpg',
    'Latin': 'Latin.jpg',
    'Literary Arts': 'LiteraryArts.jpg',
    'Logo': 'Logo.png',
    'Media': 'Media.jpg',
    'Medical': 'Medical.jpg',
    'Medicine': 'Medicine.jpg',
    'Medieval': 'Medieval.jpg',
    'Mental Health': 'MentalHealth.jpg',
    'Metal': 'Metal.jpg',
    'Mobile': 'Mobile.jpg',
    'Mormonism': 'Mormonism.jpg',
    'Motorcycle/ATV': 'MotorcycleATV.jpg',
    'Motorsports': 'Motorsports.jpg',
    'Mountain Biking': 'MountainBiking.jpg',
    'Music': 'Music.jpg',
    'Musical': 'Musical.jpg',
    'Mysticism & Occult': 'MysticismOccult.jpg',
    'Nationality': 'Nationality.jpg',
    'New Age': 'NewAge.jpg',
    'New Years Eve': 'NewYearsEve.jpg',
    'Non Profit & NGOs': 'NonProfitNGOs.jpg',
    'Non-partisan': 'Non-partisan.jpg',
    'Obstacles': 'Obstacles.jpg',
    'Opera': 'Opera.jpg',
    'Orchestra': 'Orchestra.jpg',
    'Other Party': 'OtherParty.jpg',
    'Other': 'Other.jpg',
    'Parenting': 'Parenting.jpg',
    'Parents Association': 'ParentsAssociation.jpg',
    'Performing & Visual Arts': 'Performing&VisualArts.jpg',
    'Personal Health': 'PersonalHealth.jpg',
    'Pets & Animals': 'Pets&Animals.jpg',
    'Photography': 'Photography.jpg',
    'Pop': 'Pop.jpg',
    'Poverty': 'Poverty.jpg',
    'R&B': 'RB.jpg',
    'Rafting': 'Rafting.jpg',
    'Real Estate': 'RealEstate.jpg',
    'Reggae': 'Reggae.jpg',
    'Religion & Spirituality': 'ReligionSpirituality.jpg',
    'Religious/Spiritual': 'ReligiousSpiritual.jpg',
    'Renaissance': 'Renaissance.jpg',
    'Republican Party': 'RepublicanParty.jpg',
    'Reunion': 'Reunion.jpg',
    'Robotics': 'Robotics.jpg',
    'Rock': 'Rock.jpg',
    'Rugby': 'Rugby.jpg',
    'Running': 'Running.jpg',
    'Sales & Marketing': 'Sales&Marketing.jpg',
    'Science & Technology': 'Science&Technology.jpg',
    'Science': 'Science.jpg',
    'Seasonal & Holiday': 'SeasonalHoliday.jpg',
    'Sikhism': 'Sikhism.jpg',
    'Snow Sports': 'SnowSports.jpg',
    'Soccer': 'Soccer.jpg',
    'Social Media': 'SocialMedia.jpg',
    'Spa': 'Spa.jpg',
    'Spirits': 'Spirits.jpg',
    'Sports & Fitness': 'SportsFitness.jpg',
    'St Patricks Day': 'StPatricksDay.jpg',
    'Startups & Small Business': 'StartupsSmallBusiness.jpg',
    'State Government': 'StateGovernment.jpg',
    'State': 'State.jpg',
    'Swimming & Water Sports': 'SwimmingWaterSports.jpg',
    'TV': 'TV.jpg',
    'Tennis': 'Tennis.jpg',
    'Thanksgiving': 'Thanksgiving.jpg',
    'Theatre': 'Theatre.jpg',
    'Travel & Outdoor': 'TravelOutdoor.jpg',
    'Travel': 'Travel.jpg',
}

PAYMENT_CURRENCY_CHOICES = [
    'AUD',
    'BRL',
    'CAD',
    'CHF',
    'CZK',
    'DKK',
    'EUR',
    'GBP',
    'HKD',
    'HUF',
    'ILS',
    'INR',
    'JPY',
    'MXN',
    'MYR',
    'NOK',
    'NZD',
    'PHP',
    'PLN',
    'RUB',
    'SEK',
    'SGD',
    'THB',
    'TWD',
    'USD'
]
