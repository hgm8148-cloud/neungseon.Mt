"""정상 랜드마크 + 야영장 상주 NPC·특별한 텐트 (2026-11-03)

정상 랜드마크 (LANDMARK[id])
- 한국 산: 자연석 정상석에 붉은/검은 글씨 (지리산 천왕봉·설악산 대청봉 등), 태백산은 천제단(돌 제단)
- 에베레스트 칼라파타르: 돌무더기 + 오색 타르초(룽다) 깃발 줄
- 후지산: 정상 비석 + 붉은 도리이 / 킬리만자로: 우후루 피크 초록 나무 표지판
- 황산: 바위에 새긴 붉은 '莲花峰' + 자물쇠가 매달린 쇠사슬 난간
- 하프돔: 마지막 오르막 케이블(쇠줄·기둥·디딤목) / 마터호른: 회른리 돌 산장
- 몽블랑: 락 블랑 산장 + 호수 / 트레치메: 로카텔리 산장 + 나무 십자가
- 토레스 델 파이네: 전망대 표지판 + 빙하 호수 / 통가리로: 레드 크레이터 표지판 + 증기
모양은 잘 알려진 실제 랜드마크를 단순한 3D 도형으로 다시 만든 것이에요 (사진을 붙인 게 아니에요).

야영장 (CAMP_NPC[id]): 산마다 상주하는 사람 한 명 + 그 산다운 텐트. 가까이 가면 손을 흔들고 한마디 해요.
"""
import json

# 정상 랜드마크: kind 와 글씨
LANDMARK = {
    'bukhansan': dict(kind='krstone', lines=['백운대', '836m'], color='#2a2620'),
    'hallasan': dict(kind='krstone', lines=['윗세오름', '1700m'], color='#2a2620'),
    'jirisan': dict(kind='krstone', lines=['지리산', '天王峰', '1915m'], color='#a3271c', big=True, back=['韓國人의 氣像', '여기서 發源되다']),
    'seoraksan': dict(kind='krstone', lines=['大靑峰', '1708m'], color='#a3271c', big=True),
    'mudeungsan': dict(kind='krstone', lines=['무등산', '瑞石臺', '1100m'], color='#2a2620'),
    'wolchulsan': dict(kind='krstone', lines=['월출산', '天皇峰', '809m'], color='#2a2620'),
    'naejangsan': dict(kind='krstone', lines=['내장산', '신선봉', '763m'], color='#2a2620'),
    'deogyusan': dict(kind='krstone', lines=['덕유산', '향적봉', '1614m'], color='#2a2620'),
    'sobaeksan': dict(kind='krstone', lines=['小白山', '毘盧峰', '1439.5m'], color='#2a2620'),
    'taebaeksan': dict(kind='altar', lines=['太白山', '1567m'], color='#2a2620'),
    'everest': dict(kind='flags'),
    'seongpanak': dict(kind='krstone', lines=['한라산', '白鹿潭', '1947m'], color='#2a2620', big=True),
    'fuji': dict(kind='fuji'),
    'kilimanjaro': dict(kind='uhuru'),
    'huangshan': dict(kind='huangshan'),
    'halfdome': dict(kind='cables'),
    'matterhorn': dict(kind='hut', wall=0x8f8a84, roof=0x5a5a5e, sign='HÖRNLIHÜTTE 3260m', flag='ch'),
    'montblanc': dict(kind='hut', wall=0x6b4a2b, roof=0x4a4c52, sign='REFUGE DU LAC BLANC 2352m', lake=True),
    'trecime': dict(kind='hut', wall=0xd8d0c0, roof=0x7a3a2a, sign='RIFUGIO LOCATELLI 2405m', cross=True),
    'torresdelpaine': dict(kind='board', sign=['MIRADOR', 'BASE LAS TORRES', '875 m'], lake=True, bg='#5a4026', fg='#f3e6c8'),
    'tongariro': dict(kind='board', sign=['RED CRATER', '1886 m'], steam=True, bg='#e8c21a', fg='#1d2a20'),
}

# 야영장 상주 NPC: 이름, 옷 색, 텐트(모양·색), 한마디 둘
CAMP_NPC = {
    'bukhansan': ('국립공원 레인저', dict(jacket=0x4f6a3a, pants=0x34383f, hat=0x4f6a3a, pack=0x2f5b4a, g='m'), ('bell', 0xb9a77c),
                  ['해 질 녘 백운대에서 보는 서울 불빛이 정말 예뻐요', '바위 구간은 난간을 꼭 잡고 천천히 오르세요']),
    'hallasan': ('오름지기 할망', dict(jacket=0x7a4b8f, pants=0x5a4a3a, hat=0xece6d8, pack=0x8f3a2a, g='f'), ('bell', 0xe8e2d2),
                 ['윗세오름 바람은 하루에도 몇 번씩 바뀌어요', '노루를 만나면 조용히 지켜봐 주세요']),
    'jirisan': ('천왕봉 산지기', dict(jacket=0xe08a2c, pants=0x2f3f5a, hat=0x2b2b2b, pack=0x2f5b4a, g='m'), ('dome', 0xe0702c),
                ['천왕봉 해돋이는 삼대가 덕을 쌓아야 본대요', '지리산은 넓으니 물을 넉넉히 챙기세요']),
    'seoraksan': ('산양 지킴이', dict(jacket=0xc8452a, pants=0x34383f, hat=0xe7b23a, pack=0x4a4a4a, g='f'), ('dome', 0xc8452a),
                  ['대청봉 바람은 한여름에도 차가워요', '운이 좋으면 바위 위에서 산양을 볼 수 있어요']),
    'mudeungsan': ('주상절리 해설사', dict(jacket=0x2f6f8f, pants=0x5a4a3a, hat=0xece6d8, pack=0xb08a3a, g='m'), ('aframe', 0x3a6a9a),
                   ['서석대 돌기둥은 아주 오래전 화산이 만든 거예요', '가을엔 억새가 은빛으로 출렁여요']),
    'wolchulsan': ('구름다리 안전요원', dict(jacket=0xe2c044, pants=0x2f3f5a, hat=0xe2c044, pack=0x2f3f5a, g='m'), ('aframe', 0xd8b030),
                   ['구름다리는 흔들려도 튼튼하니 걱정 마세요', '월출산 달은 바위 사이로 떠올라요']),
    'naejangsan': ('단풍 사진가', dict(jacket=0x8a7a60, pants=0x1f1f22, hat=0xc8452a, pack=0x4a4a4a, g='f'), ('bell', 0xd8822c),
                   ['내장산 단풍은 잎이 작고 유난히 붉어요', '아침 햇살에 단풍이 제일 고와요']),
    'deogyusan': ('향적봉 대피소지기', dict(jacket=0x4f8a5b, pants=0x34383f, hat=0x2b2b2b, pack=0x2f5b4a, g='m'), ('dome', 0x4f8a5b),
                  ['겨울엔 주목에 상고대가 하얗게 피어요', '곤돌라 소리가 들리면 설천봉이 가까운 거예요']),
    'sobaeksan': ('철쭉 지기', dict(jacket=0xd9688a, pants=0x34383f, hat=0xece6d8, pack=0x6a4a8a, g='f'), ('bell', 0xe7a0b4),
                  ['늦봄엔 능선 가득 철쭉이 분홍빛이에요', '소백산 바람은 세니 모자를 꼭 잡으세요']),
    'taebaeksan': ('천제단 지기', dict(jacket=0xece6d8, pants=0x5a4a3a, hat=0x2b2b2b, pack=0x4a4a4a, g='m'), ('bell', 0xf0ece0),
                   ['천제단은 옛사람들이 하늘에 제사를 올리던 곳이에요', '살아 천 년 죽어 천 년, 주목 군락을 꼭 보고 가세요']),
    'everest': ('셰르파 텐징', dict(jacket=0xe2c044, pants=0x1f1f22, hat=0xc8452a, pack=0x8f3a2a, g='m'), ('dome', 0xf0c020),
                ['나마스테! 여기서 보는 에베레스트가 제일 가까워요', '고산에선 천천히 걷고 물을 자주 마셔야 해요']),
    'fuji': ('산장 주인 야마다', dict(jacket=0x3b4f8f, pants=0x34383f, hat=0xece6d8, pack=0x4a4a4a, g='m'), ('aframe', 0xb83a2a),
             ['고라이코 해돋이는 꼭 보고 가세요', '화산 자갈은 미끄러우니 발밑을 조심해요']),
    'kilimanjaro': ('포터 바라카', dict(jacket=0x4f8a5b, pants=0x1f1f22, hat=0xe2c044, pack=0xb08a3a, g='m'), ('dome', 0x3f8a4a),
                    ['잠보! 폴레 폴레, 천천히 가야 정상에 닿아요', '아침이면 구름바다 위로 아프리카가 펼쳐져요']),
    'matterhorn': ('산악 가이드 루카', dict(jacket=0xc8452a, pants=0x2f3f5a, hat=0x2b2b2b, pack=0x4a4a4a, g='m'), ('aframe', 0xd03a2a),
                   ['산장에서 올려다보는 마터호른은 정말 압도적이에요', '알프스 날씨는 금방 바뀌니 겉옷을 챙기세요']),
    'montblanc': ('목동 장', dict(jacket=0x5a4a3a, pants=0x34383f, hat=0x8a7a60, pack=0x5a4a3a, g='m'), ('bell', 0xe8e2d2),
                  ['호수에 몽블랑이 비치면 소원을 빌어 보세요', '마멋 휘파람이 들리면 가만히 둘러보세요']),
    'trecime': ('로카텔리 산장지기', dict(jacket=0xe08a2c, pants=0x34383f, hat=0x2f6f8f, pack=0x2f5b4a, g='f'), ('aframe', 0xe07a2c),
                ['세 봉우리는 해 질 녘 붉게 물들어요', '바위에는 옛 전쟁 때 판 동굴이 아직 남아 있어요']),
    'halfdome': ('파크 레인저 에이미', dict(jacket=0x8a7a60, pants=0x4a5a40, hat=0x8a7a60, pack=0x4a5a40, g='f'), ('dome', 0x2f6f8f),
                 ['케이블 구간에선 장갑을 끼고 한 걸음씩 천천히요', '천둥이 치면 바로 내려가야 해요']),
    'huangshan': ('짐꾼 왕 씨', dict(jacket=0x3b4f8f, pants=0x1f1f22, hat=0xc8a050, pack=0x8f3a2a, g='m'), ('bell', 0xb8382a),
                  ['황산 소나무는 바위틈에서 수백 년을 버텨 왔어요', '운해가 몰려오면 봉우리들이 섬처럼 떠요']),
    'torresdelpaine': ('가우초 마테오', dict(jacket=0x8f3a2a, pants=0x5a4a3a, hat=0x2b2b2b, pack=0x5a4a3a, g='m'), ('bell', 0xcdbb94),
                       ['파타고니아 바람은 사람도 넘어뜨릴 만큼 세요', '해 뜰 무렵 세 탑이 붉게 타오르는 걸 꼭 보세요']),
    'tongariro': ('마오리 가이드 아로하', dict(jacket=0x2b2b2b, pants=0x34383f, hat=0xc8452a, pack=0x2f5b4a, g='f'), ('aframe', 0x4f8a5b),
                  ['키아 오라! 이 산은 마오리에게 신성한 곳이에요', '에메랄드 호수 빛은 화산 광물 때문이에요']),
}

# 번역 (ko → en, ja, zh). NPC 한마디는 '🏕 이름 · 말' 한 줄로 보여요
TR = {
    '국립공원 레인저': ('Park Ranger', 'パークレンジャー', '国家公园护林员'),
    '오름지기 할망': ('Grandma of the Oreum', 'オルムの番人のおばあさん', '火山丘守护奶奶'),
    '천왕봉 산지기': ('Cheonwangbong Warden', '天王峰の山守り', '天王峰守山人'),
    '산양 지킴이': ('Goral Keeper', 'カモシカの見守り人', '斑羚守护者'),
    '주상절리 해설사': ('Rock Column Guide', '柱状節理の解説員', '柱状节理解说员'),
    '구름다리 안전요원': ('Cloud Bridge Guard', '雲の橋の安全係', '云桥安全员'),
    '단풍 사진가': ('Autumn Leaf Photographer', '紅葉写真家', '红叶摄影师'),
    '향적봉 대피소지기': ('Hyangjeokbong Shelter Keeper', '香積峰避難所の番人', '香积峰避难所管理员'),
    '철쭉 지기': ('Azalea Keeper', 'ツツジの番人', '杜鹃守护人'),
    '천제단 지기': ('Altar Keeper', '天祭壇の番人', '天祭坛守护人'),
    '셰르파 텐징': ('Tenzing the Sherpa', 'シェルパのテンジン', '夏尔巴人丹增'),
    '산장 주인 야마다': ('Mr. Yamada, Hut Owner', '山小屋の主人・山田さん', '山屋主人山田'),
    '포터 바라카': ('Baraka the Porter', 'ポーターのバラカ', '背夫巴拉卡'),
    '산악 가이드 루카': ('Luca, Mountain Guide', '山岳ガイドのルカ', '登山向导卢卡'),
    '목동 장': ('Jean the Shepherd', '羊飼いのジャン', '牧羊人让'),
    '로카텔리 산장지기': ('Locatelli Hut Keeper', 'ロカテッリ小屋の番人', '洛卡泰利小屋管理员'),
    '파크 레인저 에이미': ('Amy, Park Ranger', 'パークレンジャーのエイミー', '公园护林员艾米'),
    '짐꾼 왕 씨': ('Mr. Wang the Porter', '荷担ぎの王さん', '挑夫老王'),
    '가우초 마테오': ('Mateo the Gaucho', 'ガウチョのマテオ', '高乔人马特奥'),
    '마오리 가이드 아로하': ('Aroha, Māori Guide', 'マオリのガイド、アロハ', '毛利向导阿萝哈'),
    '해 질 녘 백운대에서 보는 서울 불빛이 정말 예뻐요': ('The lights of Seoul from Baegundae at dusk are lovely', '夕暮れの白雲台から見るソウルの灯りは本当にきれいです', '黄昏时从白云台看首尔的灯火真美'),
    '바위 구간은 난간을 꼭 잡고 천천히 오르세요': ('Hold the railing and go slowly on the rock sections', '岩場では手すりをしっかり握ってゆっくり登ってください', '岩石路段请抓紧栏杆慢慢爬'),
    '윗세오름 바람은 하루에도 몇 번씩 바뀌어요': ('The wind at Witsae-oreum changes many times a day', 'ウィッセオルムの風は一日に何度も変わります', '威势岳的风一天要变好几次'),
    '노루를 만나면 조용히 지켜봐 주세요': ('If you meet a roe deer, just watch quietly', 'ノロジカに会ったら静かに見守ってください', '遇到狍子请安静地看着它'),
    '천왕봉 해돋이는 삼대가 덕을 쌓아야 본대요': ('They say it takes three generations of good deeds to see sunrise on Cheonwangbong', '天王峰の日の出は三代が徳を積まないと見られないそうです', '据说要三代积德才能看到天王峰日出'),
    '지리산은 넓으니 물을 넉넉히 챙기세요': ('Jirisan is vast, so bring plenty of water', '智異山は広いので水を多めに持ってください', '智异山很大，请多带些水'),
    '대청봉 바람은 한여름에도 차가워요': ('The wind on Daecheongbong is cold even in midsummer', '大青峰の風は真夏でも冷たいです', '大青峰的风即使在盛夏也很冷'),
    '운이 좋으면 바위 위에서 산양을 볼 수 있어요': ('With luck you may see a goral on the rocks', '運が良ければ岩の上にカモシカが見られます', '运气好的话能在岩石上看到斑羚'),
    '서석대 돌기둥은 아주 오래전 화산이 만든 거예요': ('The stone columns of Seoseokdae were made by an ancient volcano', '瑞石台の石柱は大昔の火山がつくったものです', '瑞石台的石柱是远古火山形成的'),
    '가을엔 억새가 은빛으로 출렁여요': ('In autumn the silver grass waves like silver', '秋にはススキが銀色に揺れます', '秋天芒草泛着银光摇曳'),
    '구름다리는 흔들려도 튼튼하니 걱정 마세요': ('The cloud bridge sways, but it is sturdy', '雲の橋は揺れても丈夫なので安心してください', '云桥虽然会晃但很结实，别担心'),
    '월출산 달은 바위 사이로 떠올라요': ('The moon over Wolchulsan rises between the rocks', '月出山の月は岩の間から昇ります', '月出山的月亮从岩石间升起'),
    '내장산 단풍은 잎이 작고 유난히 붉어요': ('Naejangsan maples have small, especially red leaves', '内蔵山の紅葉は葉が小さく、ひときわ赤いです', '内藏山的枫叶小巧而格外鲜红'),
    '아침 햇살에 단풍이 제일 고와요': ('The leaves look best in the morning sun', '朝日に照らされた紅葉がいちばんきれいです', '晨光中的红叶最美'),
    '겨울엔 주목에 상고대가 하얗게 피어요': ('In winter, rime frost blooms white on the yews', '冬にはイチイに霧氷が白く咲きます', '冬天紫杉上会结满白色雾凇'),
    '곤돌라 소리가 들리면 설천봉이 가까운 거예요': ('When you hear the gondola, Seolcheonbong is near', 'ゴンドラの音が聞こえたら雪川峰は近いです', '听到缆车声就离雪川峰不远了'),
    '늦봄엔 능선 가득 철쭉이 분홍빛이에요': ('In late spring the ridge turns pink with azaleas', '晩春には尾根一面がツツジでピンク色になります', '晚春时山脊开满粉色杜鹃'),
    '소백산 바람은 세니 모자를 꼭 잡으세요': ('The wind on Sobaeksan is strong, hold on to your hat', '小白山の風は強いので帽子をしっかり押さえて', '小白山风大，请抓紧帽子'),
    '천제단은 옛사람들이 하늘에 제사를 올리던 곳이에요': ('Cheonjedan is where people of old made offerings to heaven', '天祭壇は昔の人々が天に祭祀を捧げた場所です', '天祭坛是古人祭天的地方'),
    '살아 천 년 죽어 천 년, 주목 군락을 꼭 보고 가세요': ('A thousand years alive, a thousand dead: don\'t miss the yew grove', '生きて千年、枯れて千年。イチイの群落をぜひ見ていって', '生千年死千年，一定要看看紫杉林'),
    '나마스테! 여기서 보는 에베레스트가 제일 가까워요': ('Namaste! Everest looks closest from here', 'ナマステ！ここから見るエベレストがいちばん近いです', '合十礼！从这里看珠峰最近'),
    '고산에선 천천히 걷고 물을 자주 마셔야 해요': ('At altitude, walk slowly and drink water often', '高所ではゆっくり歩き、水をこまめに飲んで', '高海拔要慢慢走，多喝水'),
    '고라이코 해돋이는 꼭 보고 가세요': ('Don\'t miss the goraikō sunrise', 'ご来光はぜひ見ていってください', '一定要看御来光日出'),
    '화산 자갈은 미끄러우니 발밑을 조심해요': ('Volcanic gravel is slippery, watch your step', '火山礫は滑りやすいので足元に気をつけて', '火山砾很滑，注意脚下'),
    '잠보! 폴레 폴레, 천천히 가야 정상에 닿아요': ('Jambo! Pole pole, slowly is how you reach the top', 'ジャンボ！ポレポレ、ゆっくり行けば山頂に着きます', '佳博！慢慢走才能登顶'),
    '아침이면 구름바다 위로 아프리카가 펼쳐져요': ('In the morning, Africa spreads out above a sea of clouds', '朝には雲海の上にアフリカが広がります', '清晨，非洲在云海之上展开'),
    '산장에서 올려다보는 마터호른은 정말 압도적이에요': ('The Matterhorn seen from the hut is overwhelming', '山小屋から見上げるマッターホルンは圧巻です', '从小屋仰望马特洪峰非常震撼'),
    '알프스 날씨는 금방 바뀌니 겉옷을 챙기세요': ('Alpine weather changes fast, bring a jacket', 'アルプスの天気はすぐ変わるので上着を持って', '阿尔卑斯天气多变，带上外套'),
    '호수에 몽블랑이 비치면 소원을 빌어 보세요': ('When Mont Blanc reflects in the lake, make a wish', '湖にモンブランが映ったら願い事をしてみて', '湖面映出勃朗峰时许个愿吧'),
    '마멋 휘파람이 들리면 가만히 둘러보세요': ('If you hear a marmot whistle, look around quietly', 'マーモットの口笛が聞こえたら静かに見回して', '听到旱獭的口哨声就静静看看四周'),
    '세 봉우리는 해 질 녘 붉게 물들어요': ('The three peaks glow red at sunset', '三つの峰は夕暮れに赤く染まります', '三座山峰在日落时被染红'),
    '바위에는 옛 전쟁 때 판 동굴이 아직 남아 있어요': ('Tunnels dug in an old war still remain in the rock', '岩には昔の戦争で掘られた洞窟がまだ残っています', '岩石里还留着旧时战争挖的洞穴'),
    '케이블 구간에선 장갑을 끼고 한 걸음씩 천천히요': ('On the cables, wear gloves and go one step at a time', 'ケーブル区間では手袋をして一歩ずつゆっくり', '钢索路段请戴手套一步一步慢慢走'),
    '천둥이 치면 바로 내려가야 해요': ('If you hear thunder, head down right away', '雷が鳴ったらすぐに下りてください', '一打雷就要马上下山'),
    '황산 소나무는 바위틈에서 수백 년을 버텨 왔어요': ('Huangshan pines have clung to the rocks for centuries', '黄山の松は岩の隙間で何百年も耐えてきました', '黄山松在石缝中坚持了数百年'),
    '운해가 몰려오면 봉우리들이 섬처럼 떠요': ('When the clouds roll in, the peaks float like islands', '雲海が押し寄せると峰々が島のように浮かびます', '云海涌来时，山峰像岛屿一样漂浮'),
    '파타고니아 바람은 사람도 넘어뜨릴 만큼 세요': ('Patagonian wind can knock a person over', 'パタゴニアの風は人を倒すほど強いです', '巴塔哥尼亚的风能把人吹倒'),
    '해 뜰 무렵 세 탑이 붉게 타오르는 걸 꼭 보세요': ('Watch the three towers burn red at sunrise', '日の出に三つの塔が赤く燃えるのをぜひ見て', '一定要看日出时三塔被染红'),
    '키아 오라! 이 산은 마오리에게 신성한 곳이에요': ('Kia ora! This mountain is sacred to the Māori', 'キア・オラ！この山はマオリにとって神聖な場所です', '奇亚奥拉！这座山对毛利人是神圣的'),
    '에메랄드 호수 빛은 화산 광물 때문이에요': ('The Emerald Lakes get their colour from volcanic minerals', 'エメラルド湖の色は火山の鉱物によるものです', '翡翠湖的颜色来自火山矿物'),
}


def lm_rows(m):
    """이 산 NPC 한마디 번역 줄 ('🏕 이름 · 말')"""
    v = CAMP_NPC.get(m['id']) or CAMP_NPC.get(m.get('base', ''))
    if not v: return []
    name, _, _, lines = v
    rows = []
    for l in lines:
        n, s = TR[name], TR[l]
        rows.append([f'🏕 {name} · {l}', f'🏕 {n[0]} · {s[0]}', f'🏕 {n[1]} · {s[1]}', f'🏕 {n[2]} · {s[2]}'])
    rows.append([name, *TR[name]])
    return rows


LM_JS = r'''
// ---------- 정상 랜드마크 (pipeline/landmark_patch.py) ----------
function landmarkTex(lines, w, h, fg, opts = {}){
  const c = document.createElement('canvas'); c.width = w; c.height = h; const x = c.getContext('2d');
  if(opts.bg){ x.fillStyle = opts.bg; x.fillRect(0,0,w,h); if(opts.frame){ x.strokeStyle = opts.frame; x.lineWidth = 14; x.strokeRect(7,7,w-14,h-14); } }
  x.textAlign = 'center'; x.textBaseline = 'middle';
  const n = lines.length, lh = h/(n+0.6);
  lines.forEach((t, i) => { const big = i === (opts.bigLine ?? (n > 2 ? 1 : 0)); let s = Math.min(lh*(big ? 0.86 : 0.6), w*0.92/Math.max(1, t.length)*(/[ㄱ-힝一-鿿]/.test(t) ? 1 : 1.7));
    x.font = `${big ? 900 : 700} ${s}px "Noto Serif KR","Gowun Batang","Noto Sans KR",serif`;
    if(opts.carve){ x.fillStyle = 'rgba(255,255,255,.25)'; x.fillText(t, w/2+2, lh*(i+0.8)+2); }
    x.fillStyle = fg; x.fillText(t, w/2, lh*(i+0.8)); });
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 4; return t;
}
function lmStone(sx, sy, sz, seed){   // 자연석 덩어리 (앞면은 글씨를 새길 수 있게 평평하게: z = 0.3*sz)
  const g = new THREE.IcosahedronGeometry(1, 3), pa = g.attributes.position;
  for(let i=0;i<pa.count;i++){ const x=pa.getX(i), y=pa.getY(i), z=pa.getZ(i); const k = 0.9 + vnoise(x*1.6+seed, z*1.6+y*1.2)*0.22; pa.setXYZ(i, x*sx*k, y*sy*k, z > 0.3 ? 0.3*sz : z*sz*k); }
  g.computeVertexNormals(); return g;
}
function buildLandmark(g, stone, face, post){
  const L = __LM__, gy = g.position.y; if(!L) return; const gpos = g.position.clone();
  const granite = new THREE.MeshStandardMaterial({ map:TEX.granite, color:0xd4d0c8, roughness:0.9 });
  const G0 = g; g = new THREE.Group(); g.rotation.y = Math.PI/2; G0.add(g);   // 올라오는 사람을 바라보게
  const add = (m, x, y, z) => { m.position.set(x, y, z); m.castShadow = true; m.receiveShadow = true; g.add(m); return m; };
  if(L.kind === 'krstone' || L.kind === 'altar'){
    stone.visible = false; face.visible = false;
    const H = L.big ? 2.3 : 1.7, W = L.big ? 1.25 : 0.95;
    add(new THREE.Mesh(lmStone(W, H/2, 0.55, 3), granite), 0, H/2 - 0.02, 0);
    // 받침돌
    add(new THREE.Mesh(lmStone(W*1.25, 0.22, 0.75, 9), granite), 0, 0.05, 0);
    const tex = landmarkTex(L.lines, 256, Math.round(256*H/W*0.82), L.color, { carve:true });
    const f = new THREE.Mesh(new THREE.PlaneGeometry(W*1.25, H*0.82), new THREE.MeshStandardMaterial({ map:tex, transparent:true, roughness:0.9, depthWrite:false, polygonOffset:true, polygonOffsetFactor:-2 }));
    add(f, 0, H*0.5, 0.3*0.55 + 0.015);
    if(L.back){ const b = new THREE.Mesh(new THREE.PlaneGeometry(W*1.2, H*0.6), new THREE.MeshStandardMaterial({ map:landmarkTex(L.back, 256, 200, L.color, {carve:true, bigLine:-1}), transparent:true, depthWrite:false, polygonOffset:true, polygonOffsetFactor:-2 })); b.rotation.y = Math.PI; add(b, 0, H*0.5, -0.55*0.95); }
    if(L.kind === 'altar'){   // 천제단: 둥글게 쌓은 돌 제단
      const ring = new THREE.Group(); ring.position.set(0, 0, -5.5); g.add(ring);
      const sm = new THREE.MeshStandardMaterial({ map:TEX.granite, color:0xa8a39a, roughness:0.95 }), sg = new THREE.DodecahedronGeometry(0.32);
      for(let lv=0; lv<4; lv++) for(let i=0;i<34;i++){ const a = i/34*6.283 + lv*0.09, r = 3.2 - lv*0.05; if(lv > 0 && Math.abs(Math.sin(a/2)) < 0.12) continue;   // 앞쪽 입구
        const s = new THREE.Mesh(sg, sm); s.position.set(Math.cos(a)*r, 0.2 + lv*0.42, Math.sin(a)*r); s.scale.set(1.25, 0.75, 0.9); s.rotation.set(Math.random(), a, Math.random()*0.3); s.castShadow = true; ring.add(s); }
      const al = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.75, 0.8), sm); al.position.set(0, 0.38, 0.4); al.castShadow = true; ring.add(al);
    }
    return;
  }
  stone.visible = false; face.visible = false;
  if(L.kind === 'uhuru'){   // 킬리만자로 우후루 피크 초록 나무 표지판
    const wd = new THREE.MeshStandardMaterial({ color:0x2f5a2a, roughness:0.8 });
    for(const x of [-1.25, 1.25]) add(new THREE.Mesh(new THREE.BoxGeometry(0.16, 3.0, 0.16), wd), x, 1.5, 0);
    const tex = landmarkTex(['CONGRATULATIONS', 'YOU ARE NOW AT', 'UHURU PEAK, TANZANIA', '5895M AMSL', "AFRICA'S HIGHEST POINT"], 512, 300, '#f2d23a', { bg:'#2f6a2e', frame:'#e8c84a', bigLine:2 });
    add(new THREE.Mesh(new THREE.BoxGeometry(2.7, 1.55, 0.08), [wd, wd, wd, wd, new THREE.MeshStandardMaterial({ map:tex, roughness:0.8 }), wd]), 0, 2.15, 0);
    return;
  }
  if(L.kind === 'fuji'){   // 정상 비석 + 붉은 도리이
    const sm = new THREE.MeshStandardMaterial({ color:0x6e6a66, roughness:0.85 });
    add(new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.4, 0.9), sm), 0, 0.2, 0);
    add(new THREE.Mesh(new THREE.BoxGeometry(0.75, 2.1, 0.4), [sm, sm, sm, sm, new THREE.MeshStandardMaterial({ map:landmarkTex(['日本最高峰', '富士山剣ヶ峰', '3776m'], 160, 440, '#1c1a18', { bg:'#7a7570' }), roughness:0.85 }), sm]), 0, 1.45, 0);
    const red = new THREE.MeshStandardMaterial({ color:0xc8361e, roughness:0.6 }), blk = new THREE.MeshStandardMaterial({ color:0x1d1b1a, roughness:0.7 });
    const tr = new THREE.Group(); tr.position.set(-3.6, 0, -1.2); tr.rotation.y = 0.3; g.add(tr);
    for(const x of [-1.1, 1.1]){ const p = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.15, 3.2, 12), red); p.position.set(x, 1.6, 0); p.castShadow = true; tr.add(p); const b = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.18, 0.3, 12), blk); b.position.set(x, 0.15, 0); tr.add(b); }
    const kasagi = new THREE.Mesh(new THREE.BoxGeometry(3.4, 0.22, 0.32), blk); kasagi.position.y = 3.3; tr.add(kasagi);
    const sh = new THREE.Mesh(new THREE.BoxGeometry(3.1, 0.18, 0.26), red); sh.position.y = 3.12; tr.add(sh);
    const nuki = new THREE.Mesh(new THREE.BoxGeometry(2.7, 0.16, 0.16), red); nuki.position.y = 2.55; tr.add(nuki);
    return;
  }
  if(L.kind === 'huangshan'){   // 바위에 새긴 붉은 글씨 + 자물쇠 쇠사슬 난간
    add(new THREE.Mesh(lmStone(1.8, 1.3, 1.1, 5), granite), 0, 1.0, -0.1);
    const f = new THREE.Mesh(new THREE.PlaneGeometry(1.6, 1.5), new THREE.MeshStandardMaterial({ map:landmarkTex(['莲花峰', '1864.8M'], 256, 240, '#c0281c', { bigLine:0 }), transparent:true, depthWrite:false, polygonOffset:true, polygonOffsetFactor:-2 }));
    add(f, 0, 1.15, 0.3*1.1 - 0.1 + 0.015);
    const steel = new THREE.MeshStandardMaterial({ color:0x5d6066, metalness:0.6, roughness:0.4 }), lockC = [0xe0b030, 0xc8452a, 0xd06a8a, 0xe8c050];
    for(let i=0;i<6;i++){ const x = -3 + i*1.2; add(new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.1, 6), steel), x, 0.55, 1.6); }
    for(let i=0;i<5;i++){ const x0 = -3 + i*1.2; const ch = new THREE.Mesh(new THREE.CylinderGeometry(0.02, 0.02, 1.2, 4), steel); ch.rotation.z = Math.PI/2; add(ch, x0 + 0.6, 0.95, 1.6);
      for(let k=0;k<7;k++){ const l = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.1, 0.03), new THREE.MeshStandardMaterial({ color:lockC[(i+k)%4], metalness:0.5, roughness:0.4 })); l.rotation.z = (Math.random()-0.5)*0.6; add(l, x0 + 0.1 + k*0.15, 0.86, 1.6); } }
    return;
  }
  if(L.kind === 'flags'){   // 돌무더기 + 오색 타르초
    const sm = new THREE.MeshStandardMaterial({ map:TEX.granite, color:0x9a9590, roughness:0.95 }), sg = new THREE.DodecahedronGeometry(0.3);
    for(let i=0;i<26;i++){ const lv = Math.floor(i/8), a = i*2.4, r = 0.75 - lv*0.22; add(new THREE.Mesh(sg, sm), Math.cos(a)*r, 0.2 + lv*0.4, Math.sin(a)*r).scale.set(1.2, 0.8, 1); }
    add(new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.06, 3.4, 6), new THREE.MeshStandardMaterial({ color:0x6b4a2b })), 0, 1.9, 0);
    const cols = [0x2a5fc8, 0xf2f2ee, 0xd8322a, 0x2e9a4a, 0xf0c22a], fg = new THREE.PlaneGeometry(0.3, 0.36);
    const FL = []; for(let s=0;s<6;s++){ const a = s/6*6.283 + 0.3, len = 7 + Math.random()*3, ex = Math.cos(a)*len, ez = Math.sin(a)*len, ey = -gy + heightAt(gpos.x + ex, gpos.z + ez) + 0.3;
      for(let k=1;k<22;k++){ const t = k/22, m = new THREE.Mesh(fg, new THREE.MeshStandardMaterial({ color:cols[k%5], side:THREE.DoubleSide, roughness:0.9 })); const sag = Math.sin(t*Math.PI)*0.6;
        m.position.set(ex*t, 3.5*(1-t) + ey*t - sag - 0.2, ez*t); m.rotation.y = -a; g.add(m); FL.push(m); } }
    window.__lmFlags = FL; return;
  }
  if(L.kind === 'cables'){   // 하프돔 케이블: 쇠기둥 두 줄 + 쇠줄 + 디딤목 (마지막 오르막)
    face.visible = false; stone.visible = false; post.visible = false;
    const steel = new THREE.MeshStandardMaterial({ color:0x8a8d92, metalness:0.7, roughness:0.35 }), wd = new THREE.MeshStandardMaterial({ color:0x7a5a3a, roughness:0.9 });
    const root = new THREE.Group(); scene.add(root); const n = trail.length, i0 = Math.max(2, n - 1 - Math.round(140/2.6));
    let prev = null;
    for(let i=i0; i<n-2; i+=1){ const p = trail[i], q = trail[Math.min(n-1, i+1)], a = Math.atan2(q.x-p.x, q.z-p.z), cx = Math.cos(a), sx = Math.sin(a);
      if(prev && Math.hypot(p.x-prev.x, p.z-prev.z) < 3) continue;
      for(const s of [-0.55, 0.55]){ const x = p.x + cx*s, z = p.z - sx*s, y = heightAt(x, z); const m = new THREE.Mesh(new THREE.CylinderGeometry(0.035, 0.035, 1.0, 6), steel); m.position.set(x, y + 0.5, z); m.castShadow = true; root.add(m);
        if(prev){ const px = prev.x + prev.cx*s, pz = prev.z - prev.sx*s, py = heightAt(px, pz) + 0.95; const v = new THREE.Vector3(x - px, y + 0.95 - py, z - pz), L2 = v.length(); const c = new THREE.Mesh(new THREE.CylinderGeometry(0.012, 0.012, L2, 4), steel); c.position.set((x+px)/2, (y+0.95+py)/2, (z+pz)/2); c.quaternion.setFromUnitVectors(new THREE.Vector3(0,1,0), v.normalize()); root.add(c); } }
      const b = new THREE.Mesh(new THREE.BoxGeometry(1.15, 0.06, 0.1), wd); b.position.set(p.x, heightAt(p.x, p.z) + 0.04, p.z); b.rotation.y = a + Math.PI/2; root.add(b);
      prev = { x:p.x, z:p.z, cx, sx }; }
    return;
  }
  if(L.kind === 'board'){   // 나무 전망대 표지판 (+호수·증기는 아래에서)
    const wd = new THREE.MeshStandardMaterial({ color:0x5a4026, roughness:0.85 });
    for(const x of [-0.85, 0.85]) add(new THREE.Mesh(new THREE.BoxGeometry(0.14, 2.2, 0.14), wd), x, 1.1, 0);
    add(new THREE.Mesh(new THREE.BoxGeometry(2.0, 1.0, 0.07), [wd, wd, wd, wd, new THREE.MeshStandardMaterial({ map:landmarkTex(L.sign, 400, 200, L.fg, { bg:L.bg, frame:'rgba(0,0,0,.35)' }), roughness:0.8 }), wd]), 0, 1.75, 0);
    return;
  }
  if(L.kind === 'hut'){ post.visible = true; face.visible = false; return; }   // 산장은 야영장 옆에 (아래)
}
// 정상 둘레의 평평한 빈터 찾기 (야영장·탐방로와 겹치지 않게)
function lmSpot(rMin, rMax, keep){
  const top = trail[trail.length-1]; let best = null, bs = 1e9;
  for(let r=rMin; r<=rMax; r+=2) for(let a=0; a<6.28; a+=0.2){ const x = top.x + Math.cos(a)*r, z = top.z + Math.sin(a)*r, h = heightAt(x, z);
    if(Math.hypot(x-CAMP.x, z-CAMP.z) < keep + 7 || nearTrail(x, z, 1).d < keep + 1.5) continue; let sl = 0;
    for(let q=0;q<8;q++){ const aa = q*0.785; sl = Math.max(sl, Math.abs(heightAt(x+Math.cos(aa)*keep, z+Math.sin(aa)*keep) - h)); }
    const sc = sl + r*0.03; if(sc < bs){ bs = sc; best = { x, z, y:h }; } }
  return best;
}
{ const L = __LM__, top = trail[trail.length-1];
  if(L && L.kind === 'hut'){ const s = lmSpot(14, 46, 5); if(s){
    const g = new THREE.Group(); g.position.set(s.x, s.y - 0.3, s.z); g.rotation.y = Math.atan2(top.x - s.x, top.z - s.z); scene.add(g);
    const wall = new THREE.MeshStandardMaterial({ color:L.wall, map:L.wall === 0x8f8a84 ? TEX.granite : null, roughness:0.9 }), roof = new THREE.MeshStandardMaterial({ color:L.roof, roughness:0.7 }), win = new THREE.MeshStandardMaterial({ color:0x26303a, emissive:0xffc070, emissiveIntensity:0, roughness:0.4 });
    const W = 9, D = 6, H = 3.6; const b = new THREE.Mesh(new THREE.BoxGeometry(W, H, D), wall); b.position.y = H/2; b.castShadow = b.receiveShadow = true; g.add(b);
    const rs = new THREE.Shape(); rs.moveTo(-D/2-0.4, 0); rs.lineTo(0, 2.2); rs.lineTo(D/2+0.4, 0); rs.lineTo(-D/2-0.4, 0);
    const rf = new THREE.Mesh(new THREE.ExtrudeGeometry(rs, { depth:W+0.6, bevelEnabled:false }), roof); rf.rotation.y = Math.PI/2; rf.position.set(-(W+0.6)/2, H, 0); rf.castShadow = true; g.add(rf);
    for(let i=0;i<4;i++){ const w = new THREE.Mesh(new THREE.PlaneGeometry(0.8, 0.9), win); w.position.set(-3 + i*2, 2.2, D/2 + 0.01); g.add(w); }
    const door = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 2.0), new THREE.MeshStandardMaterial({ color:0x4a3020 })); door.position.set(0, 1.0, D/2 + 0.02); g.add(door);
    const sign = new THREE.Mesh(new THREE.PlaneGeometry(4.2, 0.6), new THREE.MeshStandardMaterial({ map:landmarkTex([L.sign], 700, 100, '#f4ead6', { bg:'#3a2a1c' }) })); sign.position.set(0, 3.15, D/2 + 0.03); g.add(sign);
    window.__lmHutWin = win;
    if(L.flag === 'ch'){ const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 6, 6), new THREE.MeshStandardMaterial({ color:0xdddddd })); pole.position.set(W/2 + 1.5, 3, D/2); g.add(pole);
      const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'); x.fillStyle = '#d52b1e'; x.fillRect(0,0,64,64); x.fillStyle = '#fff'; x.fillRect(26,12,12,40); x.fillRect(12,26,40,12);
      const fl = new THREE.Mesh(new THREE.PlaneGeometry(1.1, 1.1), new THREE.MeshStandardMaterial({ map:new THREE.CanvasTexture(c), side:THREE.DoubleSide })); fl.position.set(W/2 + 2.1, 5.4, D/2); g.add(fl); }
    if(L.cross){ const wd = new THREE.MeshStandardMaterial({ color:0x5a3e26 }); const v = new THREE.Mesh(new THREE.BoxGeometry(0.2, 3.4, 0.2), wd), h = new THREE.Mesh(new THREE.BoxGeometry(1.6, 0.2, 0.2), wd);
      v.position.set(-W/2 - 4, 1.7, 2); h.position.set(-W/2 - 4, 2.6, 2); v.castShadow = h.castShadow = true; g.add(v, h); }
  } }
  // 호수 (몽블랑 락 블랑·토레스 빙하 호수)
  if(L && L.lake){ const s = lmSpot(22, 70, 9); if(s){ const lk = new THREE.Mesh(new THREE.CircleGeometry(9, 48), new THREE.MeshStandardMaterial({ color:L.kind === 'board' ? 0x4fa7a8 : 0x3f7f9a, roughness:0.05, metalness:0.3, transparent:true, opacity:0.9 }));
    lk.rotation.x = -Math.PI/2; lk.scale.set(1, 0.7, 1); lk.position.set(s.x, s.y + 0.25, s.z); lk.renderOrder = 2; scene.add(lk); } }
  // 통가리로: 붉은 분화구 증기
  if(L && L.steam){ const c = document.createElement('canvas'); c.width = c.height = 64; const x = c.getContext('2d'); const gr = x.createRadialGradient(32,32,0,32,32,32); gr.addColorStop(0,'rgba(255,255,255,.7)'); gr.addColorStop(1,'rgba(255,255,255,0)'); x.fillStyle = gr; x.fillRect(0,0,64,64);
    const tex = new THREE.CanvasTexture(c), s = lmSpot(10, 30, 3), P = []; if(s){ for(let i=0;i<14;i++){ const sp = new THREE.Sprite(new THREE.SpriteMaterial({ map:tex, transparent:true, depthWrite:false, opacity:0 })); sp.userData = { t:Math.random()*4 }; sp.position.set(s.x, s.y, s.z); scene.add(sp); P.push(sp); } window.__lmSteam = { P, s }; } }
}
// 야영장 상주 NPC + 특별한 텐트
window.__campNpc = (()=>{ const N = __NPC__; if(!N) return null;
  // 텐트: 야영장 둘레에서 앉을 자리와 겹치지 않는 곳
  let tx = 0, tz = 0, best = 1e9; for(let a=0; a<6.28; a+=0.25){ const x = CAMP.x + Math.cos(a)*7.5, z = CAMP.z + Math.sin(a)*7.5; if(nearTrail(x, z, 1).d < 3) continue; let sl = 0; for(let q=0;q<6;q++){ const aa = q*1.047; sl = Math.max(sl, Math.abs(heightAt(x+Math.cos(aa)*2, z+Math.sin(aa)*2) - heightAt(x, z))); } if(sl < best){ best = sl; tx = x; tz = z; } }
  const ty = heightAt(tx, tz), face = Math.atan2(CAMP.x - tx, CAMP.z - tz), col = new THREE.Color(N.tent[1]);
  const tg = new THREE.Group(); tg.position.set(tx, ty - 0.05, tz); tg.rotation.y = face; scene.add(tg);
  const cloth = new THREE.MeshStandardMaterial({ color:col, roughness:0.85, side:THREE.DoubleSide }), dark = new THREE.MeshStandardMaterial({ color:col.clone().multiplyScalar(0.35), roughness:0.9, side:THREE.DoubleSide });
  if(N.tent[0] === 'bell'){ const c = new THREE.Mesh(new THREE.CylinderGeometry(2.0, 2.0, 0.9, 24, 1, true), cloth); c.position.y = 0.45; tg.add(c); const r = new THREE.Mesh(new THREE.ConeGeometry(2.05, 2.0, 24, 1, true), cloth); r.position.y = 1.9; tg.add(r);
    const door = new THREE.Mesh(new THREE.PlaneGeometry(0.9, 1.3), dark); door.position.set(0, 0.75, 1.98); tg.add(door); const pole = new THREE.Mesh(new THREE.CylinderGeometry(0.04, 0.04, 3.2, 6), new THREE.MeshStandardMaterial({ color:0x6b4a2b })); pole.position.y = 1.6; tg.add(pole); }
  else if(N.tent[0] === 'dome'){ const d = new THREE.Mesh(new THREE.SphereGeometry(1.6, 24, 12, 0, Math.PI*2, 0, Math.PI/2), cloth); d.scale.set(1.15, 0.85, 1); tg.add(d);
    const pm = new THREE.MeshStandardMaterial({ color:0x2b2b2b }); for(const r of [0.7, -0.7]){ const a = new THREE.Mesh(new THREE.TorusGeometry(1.62, 0.03, 6, 30, Math.PI), pm); a.rotation.set(0, r, 0); a.scale.set(1.15, 0.85, 1); tg.add(a); }
    const vest = new THREE.Mesh(new THREE.SphereGeometry(0.9, 16, 8, 0, Math.PI*2, 0, Math.PI/2), dark); vest.position.set(0, 0, 1.4); vest.scale.set(1, 1.1, 0.7); tg.add(vest); }
  else { const s = new THREE.Shape(); s.moveTo(-1.5, 0); s.lineTo(0, 1.9); s.lineTo(1.5, 0); s.lineTo(-1.5, 0); const a = new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth:3.2, bevelEnabled:false }), cloth); a.position.z = -1.6; tg.add(a);
    const door = new THREE.Mesh(new THREE.PlaneGeometry(1.0, 1.2), dark); door.position.set(0, 0.6, 1.61); tg.add(door); }
  tg.traverse(o => { if(o.isMesh){ o.castShadow = true; o.receiveShadow = true; } });
  // 랜턴 (밤에 켜져요)
  const lantern = new THREE.PointLight(0xffb060, 0, 9, 1.6); lantern.position.set(tx + Math.sin(face)*2.4, ty + 1.3, tz + Math.cos(face)*2.4); scene.add(lantern);
  const lb = new THREE.Mesh(new THREE.SphereGeometry(0.09, 10, 8), new THREE.MeshBasicMaterial({ color:0xffd28a })); lb.position.copy(lantern.position); scene.add(lb);
  // 사람: 텐트 앞에 서 있어요
  const h = makeHiker(N.outfit); scene.add(h.group); const nx = tx + Math.sin(face)*2.6 + Math.cos(face)*0.9, nz = tz + Math.cos(face)*2.6 - Math.sin(face)*0.9;
  h.group.position.set(nx, standY(nx, nz), nz); h.group.rotation.y = face;
  let waveT = 0, cool = 0, li = 0, near = false;
  return { x:nx, z:nz, h, update(dt){
    const d = Math.hypot(st.x - nx, st.z - nz); cool = Math.max(0, cool - dt); waveT = Math.max(0, waveT - dt);
    if(d < 5 && !near){ near = true; if(cool <= 0){ cool = 30; waveT = 2.2; toast('🏕 ' + N.name + ' · ' + N.lines[li++ % N.lines.length], 5); } }
    if(d > 8) near = false;
    if(d < 12){ const want = Math.atan2(st.x - nx, st.z - nz); let da = want - h.group.rotation.y; da = Math.atan2(Math.sin(da), Math.cos(da)); h.group.rotation.y += da*Math.min(1, dt*2); }
    animHiker(h, performance.now()/1000*0.4, 0, false, waveT, 0, null);
    const night = SKY.night || 0; lantern.intensity = 2.2*night; lb.visible = night > 0.2;
    if(window.__lmHutWin) window.__lmHutWin.emissiveIntensity = 1.3*night;
    if(window.__lmFlags){ const t = performance.now()/1000; window.__lmFlags.forEach((m, i) => { m.rotation.x = Math.sin(t*3 + i*0.7)*0.35; }); }
    if(window.__lmSteam){ const S = window.__lmSteam; for(const sp of S.P){ sp.userData.t += dt; const k = (sp.userData.t % 4)/4; sp.position.set(S.s.x + Math.sin(sp.userData.t*0.7)*0.8*k, S.s.y + 0.3 + k*7, S.s.z + Math.cos(sp.userData.t*0.5)*0.8*k); sp.scale.setScalar(1 + k*5); sp.material.opacity = 0.45*Math.sin(k*Math.PI); } }
  } };
})();
'''


def patch_landmark(P, m):
    L = LANDMARK.get(m['id']) or LANDMARK.get(m.get('base', ''))
    N = CAMP_NPC.get(m['id']) or CAMP_NPC.get(m.get('base', ''))
    npc = None
    if N:
        name, outfit, tent, lines = N
        npc = dict(name=name, outfit=outfit, tent=list(tent), lines=lines)
    js = LM_JS.replace('__LM__', json.dumps(L, ensure_ascii=False)).replace('__NPC__', json.dumps(npc, ensure_ascii=False))
    # 1) 정상석 자리에서 랜드마크 만들기
    P.rep("    face.position.set(0,0.95,0.26); g.add(face);", "    face.position.set(0,0.95,0.26); g.add(face); buildLandmark(g, stone, face, post);", 1)
    # 2) 함수·야영장 것들은 야영장(CAMP)이 생긴 뒤에
    P.rep("window.__game = {", js + "window.__game = {", 1)
    P.rep("updateNPCs(dt); updateRemotes(dt);", "updateNPCs(dt); updateRemotes(dt); if(window.__campNpc) window.__campNpc.update(dt);", 1)
