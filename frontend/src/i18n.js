// UI text. Odia ('or') is the primary language; English ('en') is the fallback
// for any key that is missing in Odia.
// NOTE: Odia text must be checked by a native speaker before the user study.

const STRINGS = {
  en: {
    app_title: 'CO CARE',
    tagline: 'Games to keep the mind active',
    who_is_playing: 'Who is playing?',
    new_player: 'New player',
    your_name: 'Your name',
    your_age: 'Your age',
    language: 'Language',
    consent_title: 'Permission',
    consent_text:
      'This app records your game scores and response times to adjust the games and for a college research project. It does not diagnose any illness. You can stop at any time.',
    consent_agree: 'I agree',
    start: 'Start',
    back: 'Back',
    choose_game: 'Choose a game',
    memory_match: 'Match the Pairs',
    memory_match_help: 'Look at the cards. Then find the two cards that are the same.',
    picture_recall: 'Remember the Pictures',
    picture_recall_help: 'Look at the pictures carefully. Then pick the ones you saw.',
    find_it: 'Find It',
    find_it_help: 'Find this picture as quickly as you can.',
    remember_these: 'Remember these pictures',
    which_did_you_see: 'Which pictures did you see?',
    find_this: 'Find this:',
    level: 'Level',
    round: 'Round',
    stop: 'Stop',
    well_done: 'Well done!',
    level_up: 'Very good! The next game will be a little harder.',
    level_down: 'Good effort! The next game will be a little easier.',
    level_same: 'Good! Play again at this level.',
    correct_answers: 'Correct answers',
    play_again: 'Play again',
    home: 'Home',
    history: 'My past games',
    no_history: 'No games played yet.',
    why: 'Why did the level change?',
    settings: 'Caregiver / researcher settings',
    content_version: 'Content',
    localized: 'Odia (local)',
    generic: 'Generic',
    difficulty_mode: 'Difficulty',
    adaptive: 'Adaptive',
    fixed: 'Fixed',
    export_data: 'Download data (CSV)',
    switch_player: 'Change player',
    listen: 'Listen',
    get_ready: 'Get ready…',
    error_server: 'Cannot reach the server. Is the backend running?',
  },
  or: {
    app_title: 'କୋ-କେୟାର',
    tagline: 'ମନକୁ ସକ୍ରିୟ ରଖିବା ପାଇଁ ଖେଳ',
    who_is_playing: 'କିଏ ଖେଳୁଛନ୍ତି?',
    new_player: 'ନୂଆ ଖେଳାଳି',
    your_name: 'ଆପଣଙ୍କ ନାମ',
    your_age: 'ଆପଣଙ୍କ ବୟସ',
    language: 'ଭାଷା',
    consent_title: 'ଅନୁମତି',
    consent_text:
      'ଏହି ଆପ୍ ଆପଣଙ୍କ ଖେଳର ସ୍କୋର ଏବଂ ଉତ୍ତର ଦେବାର ସମୟ ସଞ୍ଚୟ କରେ, ଖେଳକୁ ଆପଣଙ୍କ ପାଇଁ ଉପଯୁକ୍ତ କରିବା ଏବଂ ଏକ କଲେଜ ଗବେଷଣା ପାଇଁ। ଏହା କୌଣସି ରୋଗ ନିର୍ଣ୍ଣୟ କରେ ନାହିଁ। ଆପଣ ଯେକୌଣସି ସମୟରେ ବନ୍ଦ କରିପାରିବେ।',
    consent_agree: 'ମୁଁ ରାଜି',
    start: 'ଆରମ୍ଭ କରନ୍ତୁ',
    back: 'ପଛକୁ',
    choose_game: 'ଏକ ଖେଳ ବାଛନ୍ତୁ',
    memory_match: 'ଯୋଡ଼ି ମିଳାନ୍ତୁ',
    memory_match_help: 'କାର୍ଡଗୁଡ଼ିକୁ ଦେଖନ୍ତୁ। ତା\'ପରେ ଦୁଇଟି ସମାନ କାର୍ଡ ଖୋଜନ୍ତୁ।',
    picture_recall: 'ଛବି ମନେ ରଖନ୍ତୁ',
    picture_recall_help: 'ଛବିଗୁଡ଼ିକୁ ଧ୍ୟାନରେ ଦେଖନ୍ତୁ। ତା\'ପରେ ଦେଖିଥିବା ଛବି ବାଛନ୍ତୁ।',
    find_it: 'ଖୋଜି ବାହାର କରନ୍ତୁ',
    find_it_help: 'ଏହି ଛବିଟିକୁ ଶୀଘ୍ର ଖୋଜନ୍ତୁ।',
    remember_these: 'ଏହି ଛବିଗୁଡ଼ିକୁ ମନେ ରଖନ୍ତୁ',
    which_did_you_see: 'ଆପଣ କେଉଁ ଛବିଗୁଡ଼ିକ ଦେଖିଥିଲେ?',
    find_this: 'ଏହାକୁ ଖୋଜନ୍ତୁ:',
    level: 'ସ୍ତର',
    round: 'ପର୍ଯ୍ୟାୟ',
    stop: 'ବନ୍ଦ କରନ୍ତୁ',
    well_done: 'ବହୁତ ଭଲ!',
    level_up: 'ବହୁତ ଭଲ! ପରବର୍ତ୍ତୀ ଖେଳ ଟିକେ କଠିନ ହେବ।',
    level_down: 'ଭଲ ଚେଷ୍ଟା! ପରବର୍ତ୍ତୀ ଖେଳ ଟିକେ ସହଜ ହେବ।',
    level_same: 'ଭଲ! ଏହି ସ୍ତରରେ ପୁଣି ଖେଳନ୍ତୁ।',
    correct_answers: 'ଠିକ୍ ଉତ୍ତର',
    play_again: 'ପୁଣି ଖେଳନ୍ତୁ',
    home: 'ମୂଳ ପୃଷ୍ଠା',
    history: 'ମୋର ପୂର୍ବ ଖେଳ',
    no_history: 'ଏପର୍ଯ୍ୟନ୍ତ କୌଣସି ଖେଳ ହୋଇନାହିଁ।',
    switch_player: 'ଖେଳାଳି ବଦଳାନ୍ତୁ',
    listen: 'ଶୁଣନ୍ତୁ',
    get_ready: 'ପ୍ରସ୍ତୁତ ହୁଅନ୍ତୁ…',
    // settings / why / export are for caregivers and researchers: English fallback is fine.
  },
}

export function t(key, lang = 'or') {
  return STRINGS[lang]?.[key] ?? STRINGS.en[key] ?? key
}

export function label(item, lang) {
  return item.label[lang] ?? item.label.en
}

export const LANGS = [
  { code: 'or', name: 'ଓଡ଼ିଆ' },
  { code: 'en', name: 'English' },
]
