"""번역 빠진 문구 채우기 (2026-11-04 점검: lc3.js 로 페이지의 한글 문자열을 모두 뽑아 T()로 확인).
- 화면에 쓰이는데 번역 표에 없던 문장: 아래 FIX 표 (영어·일본어·중국어 + 해외 산 현지어)
- 문장을 이어 붙여 만들던 곳(하산 완료 창, 하산 중 배너, 낮과 밤 버튼 이름, 구글 로그인 문구)은 조각마다 번역해서 붙여요
- 관리자 패널은 승연 님만 쓰는 화면이라 한국어 그대로 둬요"""
import re

# [한국어, en, ja, zh, de, fr, it, es, ne, sw]
FIX = [
    ['야영을 마쳤어요. 시간이 지금 시각으로 돌아가요', 'Camp is over. The clock returns to the current time', 'キャンプを終えました。時間が今の時刻に戻ります', '露营结束了，时间回到现在', 'Das Lager ist beendet. Die Zeit springt zurück auf jetzt', 'Le bivouac est terminé. L’heure revient à maintenant', 'Il campeggio è finito. L’ora torna a quella attuale', 'El campamento terminó. La hora vuelve a la actual', 'शिविर सकियो। समय अहिलेको समयमा फर्कियो', 'Kambi limekwisha. Saa inarudi kwa wakati wa sasa'],
    ['타닥타닥… 불멍 중', 'Crackle, crackle… gazing into the fire', 'パチパチ…焚き火をぼんやり眺め中', '噼啪噼啪…正在发呆看火', 'Knister, knister… ins Feuer schauen', 'Crépitements… on contemple le feu', 'Crepitio… si guarda il fuoco', 'Crepita, crepita… mirando el fuego', 'चटचट… आगो हेर्दै', 'Kwacha kwacha… ukitazama moto'],
    ['은하수가 머리 위로 흘러요 · 가끔 별똥별도 떨어져요', 'The Milky Way flows overhead · a shooting star falls now and then', '天の川が頭上を流れます · ときどき流れ星も', '银河在头顶流淌 · 偶尔还有流星划过', 'Die Milchstraße zieht über dich hinweg · ab und zu fällt eine Sternschnuppe', 'La Voie lactée s’écoule au-dessus de vous · parfois une étoile filante', 'La Via Lattea scorre sopra di te · ogni tanto cade una stella', 'La Vía Láctea fluye sobre ti · de vez en cuando cae una estrella fugaz', 'टाउकोमाथि आकाशगंगा बग्छ · कहिलेकाहीँ खसेको तारा पनि', 'Njia ya Maziwa inapita juu · mara kwa mara kimondo kinaanguka'],
    ['해가 지면 은하수가 보여요', 'The Milky Way appears after sunset', '日が沈むと天の川が見えます', '太阳落山后就能看到银河', 'Nach Sonnenuntergang erscheint die Milchstraße', 'La Voie lactée apparaît après le coucher du soleil', 'Dopo il tramonto appare la Via Lattea', 'La Vía Láctea aparece al anochecer', 'घाम अस्ताएपछि आकाशगंगा देखिन्छ', 'Njia ya Maziwa huonekana jua likizama'],
    ['지금 시각 그대로', 'Real time', '今の時刻のまま', '跟随当前时间', 'Echtzeit', 'Heure réelle', 'Ora reale', 'Hora real', 'वास्तविक समय', 'Wakati halisi'],
    ['야영 중에는 밤하늘이 이어져요', 'The night sky stays while you camp', 'キャンプ中は夜空が続きます', '露营时一直是夜空', 'Beim Zelten bleibt der Nachthimmel', 'Le ciel nocturne reste pendant le bivouac', 'Durante il campeggio resta il cielo notturno', 'Mientras acampas sigue el cielo nocturno', 'शिविरमा रहँदा रातको आकाश रहन्छ', 'Ukiwa kambini anga la usiku linaendelea'],
    ['지금 밤하늘에 별똥별이 쏟아져요 ☄️', 'Shooting stars are pouring across the night sky ☄️', '今、夜空に流れ星が降り注いでいます ☄️', '此刻夜空中流星如雨 ☄️', 'Gerade regnet es Sternschnuppen ☄️', 'Une pluie d’étoiles filantes en ce moment ☄️', 'Proprio ora piovono stelle cadenti ☄️', 'Ahora mismo llueven estrellas fugaces ☄️', 'अहिले रातको आकाशमा तारा खसिरहेका छन् ☄️', 'Sasa hivi vimondo vinamiminika angani ☄️'],
    ['지금 북쪽 하늘에 오로라가 떴어요', 'An aurora has appeared in the northern sky', '今、北の空にオーロラが出ています', '此刻北方天空出现了极光', 'Am Nordhimmel leuchtet gerade ein Polarlicht', 'Une aurore est apparue dans le ciel du nord', 'Un’aurora è apparsa nel cielo a nord', 'Ha aparecido una aurora en el cielo del norte', 'उत्तरी आकाशमा अरोरा देखियो', 'Aurora imetokea angani upande wa kaskazini'],
    ['📣 능선 소식', '📣 Neungseon news', '📣 稜線からのお知らせ', '📣 稜线消息', '📣 Neuigkeiten von Neungseon', '📣 Nouvelles de Neungseon', '📣 Notizie da Neungseon', '📣 Noticias de Neungseon', '📣 नेउङसोन समाचार', '📣 Habari za Neungseon'],
    ['텐트에 들어가 잠을 청해요…', 'You crawl into the tent to sleep…', 'テントに入って眠ります…', '钻进帐篷睡觉…', 'Du kriechst zum Schlafen ins Zelt…', 'Vous vous glissez dans la tente pour dormir…', 'Ti infili nella tenda per dormire…', 'Te metes en la tienda a dormir…', 'सुत्न पालभित्र पस्नुहुन्छ…', 'Unaingia hemani kulala…'],
    ['하산 완료', 'Descent complete', '下山完了', '下山完成', 'Abstieg geschafft', 'Descente terminée', 'Discesa completata', 'Descenso completado', 'ओरालो पूरा', 'Kushuka kumekamilika'],
    ['오늘 산행 끝!', 'that’s today’s hike!', '今日の山行はおしまい！', '今天的登山结束啦！', 'die Wanderung für heute ist geschafft!', 'fin de la randonnée du jour !', 'escursione di oggi conclusa!', '¡fin de la ruta de hoy!', 'आजको पदयात्रा सकियो!', 'safari ya leo imekwisha!'],
    ['하산 중', 'Descending', '下山中', '下山中', 'Im Abstieg', 'En descente', 'In discesa', 'Bajando', 'ओर्लँदै', 'Unashuka'],
    ['낮과 밤', 'Day & night', '昼と夜', '白天与夜晚', 'Tag & Nacht', 'Jour et nuit', 'Giorno e notte', 'Día y noche', 'दिन र रात', 'Mchana na usiku'],
    ['구글 계정', 'Google account', 'Googleアカウント', 'Google 账号', 'Google-Konto', 'Compte Google', 'Account Google', 'Cuenta de Google', 'गुगल खाता', 'Akaunti ya Google'],
    ['산행 기록이 여러 기기에 저장돼요', 'your hikes are saved across devices', '山行の記録が複数の端末に保存されます', '登山记录会保存到多台设备', 'deine Wanderungen werden geräteübergreifend gespeichert', 'vos randonnées sont enregistrées sur tous vos appareils', 'le tue escursioni sono salvate su tutti i dispositivi', 'tus rutas se guardan en todos tus dispositivos', 'तपाईंका पदयात्रा धेरै उपकरणमा सुरक्षित हुन्छन्', 'safari zako zinahifadhiwa kwenye vifaa vyote'],
    # 앱 설치 안내 (한 줄씩 통째로 번역되게 문장을 나눴어요)
    ['📲 앱으로 설치', '📲 Install as app', '📲 アプリとして追加', '📲 安装为应用', '📲 Als App installieren', '📲 Installer l’appli', '📲 Installa come app', '📲 Instalar como app', '📲 एपको रूपमा राख्नुहोस्', '📲 Sakinisha kama programu'],
    ['홈 화면에 두고 앱처럼 꽉 찬 화면으로 즐겨요', 'Keep it on your home screen and play full screen like an app', 'ホーム画面に置いて、アプリのように全画面で', '放到主屏幕，像应用一样全屏游玩', 'Auf dem Startbildschirm ablegen und wie eine App im Vollbild spielen', 'Placez-la sur l’écran d’accueil et jouez en plein écran comme une appli', 'Mettila nella schermata Home e gioca a schermo intero come un’app', 'Ponla en la pantalla de inicio y juega a pantalla completa como una app', 'होम स्क्रिनमा राखेर एपजस्तै पूरा स्क्रिनमा खेल्नुहोस्', 'Iweke kwenye skrini ya mwanzo ucheze skrini nzima kama programu'],
    ['아이폰에 앱으로 설치하기', 'Install on iPhone', 'iPhoneにアプリとして追加', '在 iPhone 上安装', 'Auf dem iPhone installieren', 'Installer sur iPhone', 'Installa su iPhone', 'Instalar en iPhone', 'आइफोनमा राख्ने तरिका', 'Sakinisha kwenye iPhone'],
    ['Safari 주소창 옆 공유 버튼을 눌러요. 안 보이면 ⋯ 버튼을 먼저 눌러요.', 'Tap the Share button next to Safari’s address bar. If you can’t see it, tap ⋯ first.', 'Safariのアドレスバー横の共有ボタンを押します。見えなければ先に ⋯ を押します。', '点击 Safari 地址栏旁的分享按钮。看不到的话先点 ⋯。', 'Tippe neben der Safari-Adressleiste auf „Teilen“. Siehst du ihn nicht, tippe zuerst auf ⋯.', 'Touchez le bouton Partager à côté de la barre d’adresse de Safari. S’il n’apparaît pas, touchez d’abord ⋯.', 'Tocca il pulsante Condividi accanto alla barra degli indirizzi di Safari. Se non lo vedi, tocca prima ⋯.', 'Toca el botón Compartir junto a la barra de direcciones de Safari. Si no lo ves, toca primero ⋯.', 'Safari को ठेगाना पट्टीछेउको सेयर बटन थिच्नुहोस्। नदेखिए पहिले ⋯ थिच्नुहोस्।', 'Gusa kitufe cha Shiriki kando ya upau wa anwani wa Safari. Kama hukioni, gusa ⋯ kwanza.'],
    ['목록을 내려 ‘홈 화면에 추가’를 눌러요.', 'Scroll down the list and tap “Add to Home Screen”.', 'リストを下にスクロールして「ホーム画面に追加」を押します。', '向下滑动列表，点击“添加到主屏幕”。', 'Scrolle nach unten und tippe auf „Zum Home-Bildschirm“.', 'Faites défiler la liste et touchez « Sur l’écran d’accueil ».', 'Scorri l’elenco e tocca “Aggiungi a Home”.', 'Desplázate por la lista y toca «Añadir a pantalla de inicio».', 'सूची तल सारेर “Add to Home Screen” थिच्नुहोस्।', 'Sogeza orodha chini na ugusa “Add to Home Screen”.'],
    ['‘웹 앱으로 열기’가 켜져 있으면 그대로 두고 ‘추가’를 눌러요.', 'Leave “Open as Web App” on and tap “Add”.', '「Webアプリとして開く」がオンならそのままで「追加」を押します。', '保持“作为网页应用打开”开启，然后点“添加”。', 'Lass „Als Web-App öffnen“ eingeschaltet und tippe auf „Hinzufügen“.', 'Laissez « Ouvrir comme app web » activé et touchez « Ajouter ».', 'Lascia attivo “Apri come web app” e tocca “Aggiungi”.', 'Deja activado «Abrir como app web» y toca «Añadir».', '“Open as Web App” खुला राखेर “Add” थिच्नुहोस्।', 'Acha “Open as Web App” ikiwa imewashwa na ugusa “Add”.'],
    ['홈 화면의 능선 아이콘으로 열면 주소창 없이 꽉 찬 화면이에요.', 'Open it from the Neungseon icon on your home screen for full screen without the address bar.', 'ホーム画面の稜線アイコンから開くと、アドレスバーのない全画面になります。', '从主屏幕的稜线图标打开，就是没有地址栏的全屏。', 'Öffnest du es über das Neungseon-Symbol, läuft es im Vollbild ohne Adressleiste.', 'Ouvrez-la depuis l’icône Neungseon pour un plein écran sans barre d’adresse.', 'Aprila dall’icona Neungseon per lo schermo intero senza barra degli indirizzi.', 'Ábrela desde el icono de Neungseon para verla a pantalla completa sin barra de direcciones.', 'होम स्क्रिनको Neungseon आइकनबाट खोल्दा ठेगाना पट्टीबिना पूरा स्क्रिन हुन्छ।', 'Ifungue kwa ikoni ya Neungseon kwenye skrini ya mwanzo upate skrini nzima bila upau wa anwani.'],
    ['카카오톡·네이버 같은 앱 안에서 연 화면에서는 설치할 수 없어요. 메뉴에서 ‘Safari로 열기’를 누른 뒤 다시 해 주세요.', 'You can’t install from inside apps like KakaoTalk or Naver. Choose “Open in Safari” from the menu and try again.', 'カカオトークやNAVERなどのアプリ内からは追加できません。メニューの「Safariで開く」を押してからもう一度どうぞ。', '在 KakaoTalk、Naver 等应用内打开时无法安装。请在菜单中选择“在 Safari 中打开”后再试。', 'In Apps wie KakaoTalk oder Naver geht das nicht. Wähle im Menü „In Safari öffnen“ und versuche es erneut.', 'Impossible depuis une appli comme KakaoTalk ou Naver. Choisissez « Ouvrir dans Safari » dans le menu, puis réessayez.', 'Non si può installare da app come KakaoTalk o Naver. Scegli “Apri in Safari” dal menu e riprova.', 'No se puede instalar desde apps como KakaoTalk o Naver. Elige «Abrir en Safari» en el menú y vuelve a intentarlo.', 'KakaoTalk वा Naver जस्ता एपभित्रबाट राख्न मिल्दैन। मेनुबाट “Open in Safari” रोजेर फेरि प्रयास गर्नुहोस्।', 'Huwezi kusakinisha ukiwa ndani ya programu kama KakaoTalk au Naver. Chagua “Open in Safari” kwenye menyu ujaribu tena.'],
    ['앱과 Safari는 기록을 따로 저장해요. 구글로 로그인하면 산행 기록이 앱으로 이어져요.', 'The app and Safari keep separate records. Sign in with Google to carry your hikes over.', 'アプリとSafariは記録を別々に保存します。Googleでログインすると記録が引き継がれます。', '应用和 Safari 分开保存记录。用 Google 登录即可同步登山记录。', 'App und Safari speichern getrennt. Mit Google-Anmeldung wandern deine Daten mit.', 'L’appli et Safari ont des données séparées. Connectez-vous avec Google pour les retrouver.', 'App e Safari salvano i dati separatamente. Accedi con Google per ritrovarli.', 'La app y Safari guardan los datos por separado. Inicia sesión con Google para conservarlos.', 'एप र Safari ले रेकर्ड छुट्टाछुट्टै राख्छन्। गुगलबाट लगइन गरे रेकर्ड सँगै आउँछ।', 'Programu na Safari huhifadhi kumbukumbu tofauti. Ingia kwa Google ili ziendelee.'],
    ['알겠어요', 'Got it', 'わかりました', '知道了', 'Verstanden', 'Compris', 'Ho capito', 'Entendido', 'बुझेँ', 'Nimeelewa'],
    ['설치했어요 · 홈 화면의 능선 아이콘으로 열어 보세요', 'Installed · open it from the Neungseon icon on your home screen', 'インストールしました · ホーム画面の稜線アイコンから開いてください', '已安装 · 请从主屏幕的稜线图标打开', 'Installiert · öffne es über das Neungseon-Symbol', 'Installée · ouvrez-la depuis l’icône Neungseon', 'Installata · aprila dall’icona Neungseon', 'Instalada · ábrela desde el icono de Neungseon', 'राखियो · होम स्क्रिनको Neungseon आइकनबाट खोल्नुहोस्', 'Imesakinishwa · ifungue kwa ikoni ya Neungseon'],
    ['📲 앱으로 설치를 누르면 홈 화면에서 바로 열 수 있어요', '📲 Tap “Install as app” to open it right from your home screen', '📲「アプリとして追加」でホーム画面からすぐ開けます', '📲 点“安装为应用”，就能从主屏幕直接打开', '📲 Mit „Als App installieren“ startest du direkt vom Startbildschirm', '📲 Touchez « Installer l’appli » pour l’ouvrir depuis l’écran d’accueil', '📲 Tocca “Installa come app” per aprirla dalla Home', '📲 Toca «Instalar como app» para abrirla desde la pantalla de inicio', '📲 “एपको रूपमा राख्नुहोस्” थिचे होम स्क्रिनबाटै खोल्न सकिन्छ', '📲 Gusa “Sakinisha kama programu” uifungue moja kwa moja'],
    ['후원', 'Support', '応援', '支持', 'Unterstützen', 'Soutenir', 'Sostieni', 'Apoyar', 'सहयोग', 'Changia'],
    ['접기', 'Fold', 'たたむ', '收起', 'Einklappen', 'Replier', 'Chiudi', 'Plegar', 'खुम्च्याउनुहोस्', 'Kunja'],
    ['펼치기', 'Open', 'ひらく', '展开', 'Ausklappen', 'Déplier', 'Apri', 'Desplegar', 'फैलाउनुहोस्', 'Fungua'],
    ['야영장 메뉴 접기·펼치기', 'Fold or open the camp menu', 'キャンプメニューをたたむ・ひらく', '收起或展开营地菜单', 'Lagermenü ein- oder ausklappen', 'Replier ou déplier le menu du bivouac', 'Chiudi o apri il menu del campo', 'Plegar o desplegar el menú del campamento', 'शिविर मेनु खुम्च्याउने वा फैलाउने', 'Kunja au fungua menyu ya kambi'],
    # 휴대폰 ⋯ 메뉴에 이름으로 보이는 버튼 설명
    ['언어 바꾸기', 'Change language', '言語を変える', '切换语言', 'Sprache ändern', 'Changer de langue', 'Cambia lingua', 'Cambiar idioma', 'भाषा बदल्नुहोस्', 'Badilisha lugha'],
    ['낮과 밤 바꾸기', 'Change day & night', '昼と夜を切り替える', '切换白天与夜晚', 'Tag & Nacht wechseln', 'Changer jour et nuit', 'Cambia giorno e notte', 'Cambiar día y noche', 'दिन र रात बदल्नुहोस्', 'Badilisha mchana na usiku'],
    ['낮과 밤: 지금 시각', 'Day & night: real time', '昼と夜：今の時刻', '白天与夜晚：当前时间', 'Tag & Nacht: Echtzeit', 'Jour et nuit : heure réelle', 'Giorno e notte: ora reale', 'Día y noche: hora real', 'दिन र रात: वास्तविक समय', 'Mchana na usiku: wakati halisi'],
]
LOCAL = ['de', 'fr', 'it', 'es', 'ne', 'sw']
from loader_patch import LOADER_FIX
from trail_patch import VP_FIX
from app_patch import PC_FIX
FIX = FIX + LOADER_FIX + VP_FIX + PC_FIX
FIX_ROWS = [r[:4] for r in FIX]
FIX_LOCAL = {l: {r[0]: r[4 + i] for r in FIX} for i, l in enumerate(LOCAL)}

INST_STEPS = r"""
  <ol class="aiSteps" id="aiSafari">
    <li><svg class="aiIc" viewBox="0 0 24 24"><path d="M12 3v12M7.5 7.5 12 3l4.5 4.5M6 11H5v10h14V11h-1"/></svg> Safari 주소창 옆 공유 버튼을 눌러요. 안 보이면 ⋯ 버튼을 먼저 눌러요.</li>
    <li>목록을 내려 ‘홈 화면에 추가’를 눌러요.</li>
    <li>‘웹 앱으로 열기’가 켜져 있으면 그대로 두고 ‘추가’를 눌러요.</li>
    <li>홈 화면의 능선 아이콘으로 열면 주소창 없이 꽉 찬 화면이에요.</li>
  </ol>
  <p class="aiNote" id="aiOther" hidden>카카오톡·네이버 같은 앱 안에서 연 화면에서는 설치할 수 없어요. 메뉴에서 ‘Safari로 열기’를 누른 뒤 다시 해 주세요.</p>"""


def patch_i18n_fix(P, m):
    # 하산 완료 창: 조각마다 번역
    P.sub(r"\$\('endT'\)\.innerHTML = '하산 완료<small>([^']*) · 오늘 산행 끝!</small>';",
          lambda mm: "$('endT').innerHTML = (window.T||(x=>x))('하산 완료') + '<small>' + (window.T||(x=>x))(%r) + ' · ' + (window.T||(x=>x))('오늘 산행 끝!') + '</small>';" % mm.group(1))
    P.rep("`하산 중 · 해발 ${Math.round(heightAt(st.x,st.z))}m`",
          "(window.T||(x=>x))('하산 중') + ' · ' + (window.T||(x=>x))(`해발 ${Math.round(heightAt(st.x,st.z))}m`)", need=False)
    P.rep("$('bTime').title = '낮과 밤: ' + label[SKY.mode];", "$('bTime').title = (window.T||(x=>x))('낮과 밤') + ': ' + (window.T||(x=>x))(label[SKY.mode]);", need=False)
    P.rep("`${(u.displayName || u.email || '구글 계정').slice(0,20)}님 · 산행 기록이 여러 기기에 저장돼요`",
          "`${(u.displayName || u.email || (window.T||(x=>x))('구글 계정')).slice(0,20)} · ${(window.T||(x=>x))('산행 기록이 여러 기기에 저장돼요')}`", need=False)
