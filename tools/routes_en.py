"""EN route answers: entry num -> (start, dest, answer-route) transcribed from the official EN booklet
Appendix II 'Routes' table."""
ROUTES_EN = {
    256: ("Marina Cove, Sai Kung", "The Duchess of Kent Children's Hospital at Sandy Bay", "Western Harbour Crossing"),
    257: ("Ko Shan Theatre, Hung Hom", "Cheung Sha Wan Plaza", "Fat Kwong Street, Soares Avenue and Argyle Street"),
    258: ("City Point, Tsuen Wan", "Mai Po Nature Reserve", "Tai Lam Tunnel and Tsing Long Highway"),
    259: ("Yuen Long Town Hall", "MOSTown, Ma On Shan", "Lam Kam Road"),
    260: ("Sha Tsui Road Playground, Tsuen Wan", "Shatin Centre", "Tai Ho Road and Cheung Pei Shan Road"),
    261: ("Nam Cheong Estate, Sham Shui Po", "Sheung Shui MTR Station", "Tsing Sha Highway and Eagle's Nest Tunnel"),
    262: ("West Kowloon Station Bus Terminus, Jordan", "Empire Hotel Hong Kong, Causeway Bay", "Hong Chong Road and Cross Harbour Tunnel"),
    263: ("Festival Walk, Kowloon Tong", "Sha Tin Town Hall", "Waterloo Road and Lion Rock Tunnel"),
    264: ("West Kowloon Xiqu Centre", "Telford Plaza, Kowloon Bay", "Chatham Road North, East Kowloon Corridor and Kai Tak Tunnel"),
    265: ("Landmark North", "Immigration Headquarters", "Fanling Highway and Tate's Cairn Tunnel"),
    266: ("United Christian Hospital", "Mong Kok District Police Station", "New Clear Water Bay Road and Prince Edward Road East"),
    267: ("Tsuen Fung Centre, Tsuen Wan", "Hong Kong Examinations and Assessment Authority, San Po Kong", "Castle Peak Road (Kwai Chung) and Lung Cheung Road"),
    268: ("Fortune Metropolis, Hung Hom", "ICAC Headquarters Building, North Point", "Cross Harbour Tunnel"),
    269: ("Academic Community Hall of Hong Kong Baptist University, Kowloon Tong", "Great Eagle Centre, Wan Chai", "Cross Harbour Tunnel"),
    270: ("Kowloon Public Library", "Happy Valley Racecourse", "Cross Harbour Tunnel"),
    271: ("K. City, Kai Tak", "Mei Foo Plaza", "Central Kowloon Bypass, Lin Cheung Road and Lai Chi Kok Road"),
    272: ("West Kowloon Government Offices", "Union Church Hong Kong, Mid-Levels", "Western Harbour Crossing, Connaught Road West Flyover and Cotton Tree Drive"),
    273: ("Manhattan Hill", "Hong Kong Science Park", "Tsing Sha Highway and Tolo Highway"),
}

# TD official EN sample route questions: id -> (start, dest, [opts in zh-opt order], ans)
SAMPLE_ROUTES_EN = {
    601: {
        'start': "Grand Promenade, Sai Wan Ho",
        'dest': "Diocesan Boys' School, Mong Kok",
        'opts': ["Via Central-Wan Chai Bypass, Connaught Road Central, Western Harbour Crossing, West Kowloon Highway and Lai Cheung Road",
                 "Via Eastern Harbour Crossing, Kwun Tong Road, Lung Cheung Road and Chuk Yuen Road",
                 "Via Gloucester Road, Cross Harbour Tunnel and Princess Margaret Road"],
        'ans': 2,
    },
    602: {
        'start': "Panda Hotel, Tsuen Wan",
        'dest': "Shun Tak Centre (Macau Ferry), Sheung Wan",
        'opts': ["Via Kwai Tsing Bridge (Tsing Yi South Bridge), Stonecutters Bridge, Tsing Sha Highway, West Kowloon Highway and Western Harbour Crossing",
                 "Via Lung Cheung Road, Chuk Yuen Road, Waterloo Road, Princess Margaret Road, Cross Harbour Tunnel and Gloucester Road",
                 "Via Kwai Chung Section of Tsing Sha Highway (Kwai Chung Bypass), West Kowloon Highway and Western Harbour Crossing"],
        'ans': 2,
    },
}
