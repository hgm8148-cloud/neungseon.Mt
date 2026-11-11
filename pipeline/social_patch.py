"""함께가기 · 인삿말 바꾸기 · 채팅 · 정상 방명록 (2026-11-06 승연)

1) 함께 가기: 같은 산(같은 방)에 있는 사람에게 제안 → 상대가 수락하면 동행.
   - 왼쪽 '함께' 버튼(사람 목록)이나 이름표를 눌러 제안, 가까이 지나가면 '함께 가기 제안' 알림이 한 번 떠요.
   - 제안·수락·거절·동행 표시는 지금 쓰는 위치 신호(rooms/<산>/peers/<uid>)에 실어 보내요 → 데이터베이스 규칙을 바꾸지 않아도 돼요.
   - 동행은 이름표·지도에 🤝 표시, '동행 따라 걷기'(자동으로 따라가기), 멀어지면 알림, 최대 4명.
2) 인삿말 바꾸기: 인사 메뉴의 '✏️ 인삿말 바꾸기'에서 5줄을 직접 고쳐요 (한 줄 20자). 다른 사람에게도 그 말이 말풍선으로 보여요.
   구글 로그인하면 다른 기기와도 같이 저장돼요.
3) 채팅: 같은 산(방)에 있는 사람끼리. 최근 50개, 하루 지나면 안 보이고 지워져요. 말한 사람 머리 위에도 말풍선.
4) 정상 방명록: 정상(야영장)에서 포스트잇을 붙여요. 산마다 한 사람 한 장(다시 쓰면 바뀜), 60자, 색 5가지.
   정상 옆에 작은 게시판이 서고, 붙은 포스트잇이 그 위에 보여요.
장난 글 막기: 욕설·링크·전화번호 거르기(보낼 때와 받을 때 둘 다), 몇 초에 한 번만(규칙에서도), 신고 3명이면 숨김,
관리자 모드(승연 님 구글 계정)에서는 바로 지우기, '이 사람 가리기'(이 기기에서 그 사람 채팅·제안 안 보기).

채팅·방명록·신고는 새 데이터베이스 자리(chat, chatlast, guest, flags)를 써서 파이어베이스 규칙을 한 번 바꿔야 해요
(pipeline/FIREBASE_RULES.md). 규칙을 바꾸기 전에는 채팅·방명록만 '아직 준비 중'으로 보이고 나머지는 그대로 동작해요.

game.template.html 은 고치지 않고 빌드할 때 덧대요.
"""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))

# 누가 쓸 수 있나: True = 구글 로그인한 사람만 (규칙 파일과 맞춰야 해요)
LOGIN_CHAT = False
LOGIN_GUEST = True

# 번역: ko, en, ja, zh, de, fr, it, es, ne, sw
SOCIAL_ROWS = [
    ['채팅', 'Chat', 'チャット', '聊天', 'Chat', 'Discussion', 'Chat', 'Chat', 'च्याट', 'Gumzo'],
    ['채팅 (Enter)', 'Chat (Enter)', 'チャット (Enter)', '聊天 (Enter)', 'Chat (Enter)', 'Discussion (Entrée)', 'Chat (Invio)', 'Chat (Intro)', 'च्याट (Enter)', 'Gumzo (Enter)'],
    ['같은 산에 있는 사람들과 이야기해요', 'Talk with people on this mountain', '同じ山にいる人と話せます', '和同一座山上的人聊天', 'Sprich mit Leuten auf diesem Berg', 'Parlez avec les gens sur cette montagne', 'Parla con chi è su questa montagna', 'Habla con la gente de esta montaña', 'यही हिमालमा भएका मानिससँग कुरा गर्नुहोस्', 'Ongea na watu walio kwenye mlima huu'],
    ['고운 말로 인사해 보세요', 'Say something kind', 'やさしい言葉でどうぞ', '说句友善的话吧', 'Sag etwas Nettes', 'Dites un mot gentil', 'Scrivi qualcosa di gentile', 'Escribe algo amable', 'राम्रो कुरा लेख्नुहोस्', 'Sema neno zuri'],
    ['보내기', 'Send', '送信', '发送', 'Senden', 'Envoyer', 'Invia', 'Enviar', 'पठाउनुहोस्', 'Tuma'],
    ['닫기', 'Close', '閉じる', '关闭', 'Schließen', 'Fermer', 'Chiudi', 'Cerrar', 'बन्द गर्नुहोस्', 'Funga'],
    ['아직 대화가 없어요. 먼저 인사를 건네 보세요.', 'No messages yet. Be the first to say hi.', 'まだ会話はありません。最初にあいさつしてみましょう。', '还没有消息，先打个招呼吧。', 'Noch keine Nachrichten. Grüß als Erste:r.', 'Pas encore de messages. Dites bonjour en premier.', 'Ancora nessun messaggio. Saluta per primo.', 'Aún no hay mensajes. Saluda primero.', 'अहिलेसम्म सन्देश छैन। पहिले नमस्कार गर्नुहोस्।', 'Bado hakuna ujumbe. Kuwa wa kwanza kusalimia.'],
    ['채팅은 구글로 로그인하면 쓸 수 있어요', 'Sign in with Google to chat', 'チャットは Google でログインすると使えます', '使用 Google 登录后即可聊天', 'Mit Google anmelden, um zu chatten', 'Connectez-vous avec Google pour discuter', 'Accedi con Google per chattare', 'Inicia sesión con Google para chatear', 'च्याट गर्न Google बाट लगइन गर्नुहोस्', 'Ingia kwa Google ili kuzungumza'],
    ['채팅과 방명록은 neungseon.com에서 열려요', 'Chat and the guestbook work on neungseon.com', 'チャットと芳名録は neungseon.com で使えます', '聊天和留言板在 neungseon.com 上可用', 'Chat und Gästebuch gibt es auf neungseon.com', 'Discussion et livre d’or sur neungseon.com', 'Chat e libro degli ospiti su neungseon.com', 'El chat y el libro de visitas funcionan en neungseon.com', 'च्याट र अतिथि पुस्तिका neungseon.com मा चल्छन्', 'Gumzo na kitabu cha wageni viko kwenye neungseon.com'],
    ['채팅을 준비하고 있어요. 곧 열려요.', 'Chat is being set up. Opening soon.', 'チャットを準備中です。もうすぐ開きます。', '聊天正在准备中，即将开放。', 'Der Chat wird vorbereitet. Bald geht’s los.', 'La discussion arrive bientôt.', 'La chat arriva presto.', 'El chat estará listo pronto.', 'च्याट तयारी हुँदैछ। छिट्टै खुल्छ।', 'Gumzo linaandaliwa. Litafunguliwa hivi karibuni.'],
    ['고운 말로 적어 주세요 · 주소(링크)와 전화번호는 쓸 수 없어요', 'Please keep it kind · links and phone numbers aren’t allowed', 'やさしい言葉でお願いします・リンクと電話番号は使えません', '请文明用语 · 不能发送链接和电话号码', 'Bitte freundlich bleiben · keine Links oder Telefonnummern', 'Restez courtois · pas de liens ni de numéros', 'Sii gentile · niente link o numeri di telefono', 'Sé amable · no se permiten enlaces ni teléfonos', 'राम्रो भाषा प्रयोग गर्नुहोस् · लिङ्क र फोन नम्बर राख्न मिल्दैन', 'Tafadhali kuwa mpole · viungo na nambari za simu haviruhusiwi'],
    ['조금 천천히 보내 주세요', 'Please slow down a little', '少しゆっくり送ってください', '请稍慢一点发送', 'Bitte etwas langsamer', 'Un peu plus lentement, s’il vous plaît', 'Un po’ più piano, per favore', 'Un poco más despacio, por favor', 'अलि बिस्तारै पठाउनुहोस्', 'Tafadhali punguza kasi kidogo'],
    ['보내지 못했어요 · 잠시 후 다시 해 주세요', 'Couldn’t send · please try again shortly', '送信できませんでした・少し後でもう一度', '发送失败 · 请稍后再试', 'Senden fehlgeschlagen · bitte gleich nochmal', 'Envoi impossible · réessayez bientôt', 'Invio non riuscito · riprova tra poco', 'No se pudo enviar · inténtalo en un momento', 'पठाउन सकिएन · केही बेरपछि फेरि प्रयास गर्नुहोस्', 'Imeshindwa kutuma · jaribu tena baadaye'],
    ['(가려진 말)', '(hidden)', '(非表示)', '(已隐藏)', '(ausgeblendet)', '(masqué)', '(nascosto)', '(oculto)', '(लुकाइएको)', '(imefichwa)'],
    ['신고하기', 'Report', '通報する', '举报', 'Melden', 'Signaler', 'Segnala', 'Denunciar', 'रिपोर्ट गर्नुहोस्', 'Ripoti'],
    ['이 사람 가리기', 'Hide this person', 'この人を非表示', '屏蔽此人', 'Diese Person ausblenden', 'Masquer cette personne', 'Nascondi questa persona', 'Ocultar a esta persona', 'यो व्यक्ति लुकाउनुहोस्', 'Ficha mtu huyu'],
    ['지우기 (관리자)', 'Delete (admin)', '削除 (管理者)', '删除 (管理员)', 'Löschen (Admin)', 'Supprimer (admin)', 'Elimina (admin)', 'Borrar (admin)', 'मेटाउनुहोस् (एडमिन)', 'Futa (msimamizi)'],
    ['신고했어요 · 여러 사람이 신고하면 가려져요', 'Reported · it will be hidden if several people report it', '通報しました・複数の人が通報すると非表示になります', '已举报 · 多人举报后将被隐藏', 'Gemeldet · bei mehreren Meldungen wird es ausgeblendet', 'Signalé · masqué si plusieurs personnes le signalent', 'Segnalato · verrà nascosto se più persone lo segnalano', 'Denunciado · se ocultará si varias personas lo denuncian', 'रिपोर्ट गरियो · धेरैले रिपोर्ट गरे लुकाइन्छ', 'Imeripotiwa · itafichwa watu kadhaa wakiripoti'],
    ['이 사람의 채팅과 제안을 더 보지 않아요', 'You won’t see this person’s chat or invites', 'この人のチャットと誘いを表示しません', '将不再显示此人的消息和邀请', 'Chat und Einladungen dieser Person werden ausgeblendet', 'Vous ne verrez plus ses messages ni invitations', 'Non vedrai più chat e inviti di questa persona', 'No verás más sus mensajes ni invitaciones', 'यो व्यक्तिको च्याट र निम्तो देखिने छैन', 'Hutaona gumzo wala mialiko ya mtu huyu'],
    ['지웠어요', 'Deleted', '削除しました', '已删除', 'Gelöscht', 'Supprimé', 'Eliminato', 'Borrado', 'मेटाइयो', 'Imefutwa'],
    # 함께 가기
    ['함께', 'Together', '一緒に', '同行', 'Zusammen', 'Ensemble', 'Insieme', 'Juntos', 'सँगै', 'Pamoja'],
    ['함께 가기', 'Hike together', '一緒に行く', '一起走', 'Zusammen gehen', 'Marcher ensemble', 'Cammina insieme', 'Ir juntos', 'सँगै जाऔँ', 'Twende pamoja'],
    ['함께 가기 제안', 'Invite to hike together', '一緒に行こうと誘う', '邀请一起走', 'Zum gemeinsamen Gehen einladen', 'Proposer de marcher ensemble', 'Invita a camminare insieme', 'Invitar a ir juntos', 'सँगै जान निम्तो', 'Alika mtembee pamoja'],
    ['같은 산에 있는 사람에게 함께 가자고 제안해 보세요. 상대가 수락하면 동행이 돼요.', 'Invite someone on this mountain to hike together. If they accept, you become companions.', '同じ山にいる人を誘ってみましょう。相手が受けると同行者になります。', '邀请同一座山上的人一起走。对方接受后就成为同伴。', 'Lade jemanden auf diesem Berg ein. Nimmt die Person an, wandert ihr zusammen.', 'Invitez quelqu’un sur cette montagne. S’il accepte, vous marchez ensemble.', 'Invita qualcuno su questa montagna. Se accetta, camminate insieme.', 'Invita a alguien de esta montaña. Si acepta, iréis juntos.', 'यही हिमालमा भएका कसैलाई सँगै जान निम्तो दिनुहोस्। स्वीकारे सँगी बन्नुहुन्छ।', 'Mwalike mtu aliye kwenye mlima huu. Akikubali, mtatembea pamoja.'],
    ['지금은 이 산에 다른 사람이 없어요', 'Nobody else is on this mountain right now', 'いまこの山にはほかに誰もいません', '现在这座山上没有其他人', 'Gerade ist sonst niemand auf diesem Berg', 'Personne d’autre sur cette montagne pour l’instant', 'Al momento non c’è nessun altro su questa montagna', 'Ahora no hay nadie más en esta montaña', 'अहिले यो हिमालमा अरू कोही छैन', 'Kwa sasa hakuna mtu mwingine mlimani'],
    ['함께 가기는 neungseon.com에서 할 수 있어요', 'Hiking together works on neungseon.com', '一緒に行く機能は neungseon.com で使えます', '一起走功能在 neungseon.com 上可用', 'Zusammen gehen geht auf neungseon.com', 'Marcher ensemble : sur neungseon.com', 'Camminare insieme funziona su neungseon.com', 'Ir juntos funciona en neungseon.com', 'सँगै जाने सुविधा neungseon.com मा छ', 'Kutembea pamoja kunafanya kazi kwenye neungseon.com'],
    ['동행', 'Companions', '同行者', '同伴', 'Begleitung', 'Compagnons', 'Compagni', 'Compañeros', 'सँगी', 'Wenzako'],
    ['동행 중', 'Together', '同行中', '同行中', 'Zusammen', 'Ensemble', 'Insieme', 'Juntos', 'सँगै', 'Pamoja'],
    ['제안했어요', 'Invited', '誘いました', '已邀请', 'Eingeladen', 'Invité', 'Invitato', 'Invitado', 'निम्तो दिइयो', 'Umealikwa'],
    ['동행 따라 걷기', 'Follow companion', '同行者について歩く', '跟随同伴', 'Begleitung folgen', 'Suivre le compagnon', 'Segui il compagno', 'Seguir al compañero', 'सँगीलाई पछ्याउनुहोस्', 'Mfuate mwenzako'],
    ['따라 걷기 멈추기', 'Stop following', 'ついて歩くのをやめる', '停止跟随', 'Nicht mehr folgen', 'Arrêter de suivre', 'Smetti di seguire', 'Dejar de seguir', 'पछ्याउन रोक्नुहोस्', 'Acha kufuata'],
    ['동행 그만하기', 'Leave the group', '同行をやめる', '结束同行', 'Gruppe verlassen', 'Quitter le groupe', 'Lascia il gruppo', 'Dejar el grupo', 'समूह छोड्नुहोस्', 'Ondoka kwenye kikundi'],
    ['님이 함께 가자고 해요', 'wants to hike together', 'さんが一緒に行こうと誘っています', '邀请你一起走', 'möchte mit dir gehen', 'vous propose de marcher ensemble', 'ti invita a camminare insieme', 'quiere ir contigo', 'सँगै जान चाहनुहुन्छ', 'anataka mtembee pamoja'],
    ['괜찮아요', 'No thanks', '大丈夫です', '不用了', 'Nein, danke', 'Non merci', 'No, grazie', 'No, gracias', 'पर्दैन, धन्यवाद', 'Hapana, asante'],
    ['님에게 함께 가기를 제안했어요', 'has been invited to hike together', 'さんを誘いました', '已收到你的同行邀请', 'wurde eingeladen', 'a été invité·e à marcher ensemble', 'è stato invitato', 'ha sido invitado', 'लाई निम्तो पठाइयो', 'amealikwa kutembea pamoja'],
    ['님과 함께 걸어요', 'is now hiking with you', 'さんと一緒に歩きます', '和你一起走了', 'geht jetzt mit dir', 'marche maintenant avec vous', 'ora cammina con te', 'ahora va contigo', 'अब तपाईंसँगै हुनुहुन्छ', 'sasa anatembea nawe'],
    ['님은 지금은 혼자 걷고 싶대요', 'would rather walk alone for now', 'さんは今は一人で歩きたいそうです', '现在想一个人走', 'möchte gerade lieber allein gehen', 'préfère marcher seul·e pour l’instant', 'preferisce camminare da solo per ora', 'prefiere caminar solo por ahora', 'अहिले एक्लै हिँड्न चाहनुहुन्छ', 'angependa kutembea peke yake kwa sasa'],
    ['님이 가까이 있어요', 'is nearby', 'さんが近くにいます', '就在附近', 'ist in der Nähe', 'est tout près', 'è qui vicino', 'está cerca', 'नजिकै हुनुहुन्छ', 'yuko karibu'],
    ['조금 뒤에 다시 제안해 주세요', 'Please wait a moment before inviting again', '少し待ってからもう一度誘ってください', '请稍后再邀请', 'Bitte kurz warten, bevor du erneut einlädst', 'Attendez un peu avant de réinviter', 'Aspetta un attimo prima di invitare di nuovo', 'Espera un poco antes de invitar otra vez', 'फेरि निम्तो दिन अलि पर्खनुहोस्', 'Subiri kidogo kabla ya kualika tena'],
    ['동행이 가득 찼어요 (최대 4명)', 'The group is full (up to 4)', '同行者がいっぱいです (最大4人)', '同伴已满 (最多4人)', 'Die Gruppe ist voll (max. 4)', 'Le groupe est complet (4 max.)', 'Il gruppo è pieno (max 4)', 'El grupo está lleno (máx. 4)', 'समूह भरियो (बढीमा ४)', 'Kikundi kimejaa (hadi 4)'],
    ['동행을 마쳤어요', 'You left the group', '同行を終えました', '已结束同行', 'Du hast die Gruppe verlassen', 'Vous avez quitté le groupe', 'Hai lasciato il gruppo', 'Has dejado el grupo', 'तपाईंले समूह छोड्नुभयो', 'Umeondoka kwenye kikundi'],
    ['동행과 멀어졌어요 · 잠시 기다려 볼까요?', 'You’re far from your companion · wait a moment?', '同行者と離れました・少し待ちましょうか?', '和同伴离远了 · 要等一等吗？', 'Deine Begleitung ist weit weg · kurz warten?', 'Votre compagnon est loin · on l’attend ?', 'Il compagno è lontano · lo aspetti un attimo?', 'Tu compañero está lejos · ¿lo esperas?', 'सँगी टाढा हुनुभयो · अलि पर्खने?', 'Mwenzako yuko mbali · subiri kidogo?'],
    ['동행이 산을 떠났어요', 'Your companion left the mountain', '同行者が山を離れました', '同伴已离开这座山', 'Deine Begleitung hat den Berg verlassen', 'Votre compagnon a quitté la montagne', 'Il compagno ha lasciato la montagna', 'Tu compañero dejó la montaña', 'सँगीले हिमाल छोड्नुभयो', 'Mwenzako ameondoka mlimani'],
    ['동행을 따라 걸어요 · 직접 움직이면 멈춰요', 'Following your companion · move yourself to stop', '同行者について歩きます・自分で動くと止まります', '正在跟随同伴 · 自己移动即可停止', 'Du folgst deiner Begleitung · selbst bewegen zum Stoppen', 'Vous suivez votre compagnon · bougez pour arrêter', 'Segui il compagno · muoviti per fermarti', 'Sigues a tu compañero · muévete para parar', 'सँगीलाई पछ्याउँदै · आफैँ चले रोकिन्छ', 'Unamfuata mwenzako · jisogeze kusimama'],
    ['구글로 로그인해야 쓸 수 있어요', 'Sign in with Google to post', 'Google でログインすると書けます', '使用 Google 登录后才能发布', 'Zum Schreiben mit Google anmelden', 'Connectez-vous avec Google pour écrire', 'Accedi con Google per scrivere', 'Inicia sesión con Google para escribir', 'लेख्न Google बाट लगइन गर्नुहोस्', 'Ingia kwa Google ili kuandika'],
    ['함께 걷는 사람이 보이면 여기에 나와요', 'People on this mountain will show up here', 'この山にいる人がここに表示されます', '这座山上的人会显示在这里', 'Leute auf diesem Berg erscheinen hier', 'Les personnes sur cette montagne apparaîtront ici', 'Qui compariranno le persone su questa montagna', 'Aquí aparecerá la gente de esta montaña', 'यो हिमालका मानिस यहाँ देखिन्छन्', 'Watu walio mlimani wataonekana hapa'],
    # 인삿말
    ['✏️ 인삿말 바꾸기', '✏️ Edit greetings', '✏️ あいさつを編集', '✏️ 编辑问候语', '✏️ Grüße bearbeiten', '✏️ Modifier les salutations', '✏️ Modifica i saluti', '✏️ Editar saludos', '✏️ अभिवादन बदल्नुहोस्', '✏️ Hariri salamu'],
    ['인삿말 바꾸기', 'Edit greetings', 'あいさつを編集', '编辑问候语', 'Grüße bearbeiten', 'Modifier les salutations', 'Modifica i saluti', 'Editar saludos', 'अभिवादन बदल्नुहोस्', 'Hariri salamu'],
    ['인사(1)를 할 때 머리 위에 보이는 말이에요. 한 줄에 20자까지 쓸 수 있어요.', 'These appear above your head when you greet (1). Up to 20 characters each.', 'あいさつ(1)のとき頭の上に出る言葉です。1行20文字まで。', '打招呼(1)时显示在头顶的话，每行最多20字。', 'Erscheint beim Grüßen (1) über deinem Kopf. Bis zu 20 Zeichen.', 'Apparaît au-dessus de votre tête quand vous saluez (1). 20 caractères max.', 'Appare sopra la testa quando saluti (1). Massimo 20 caratteri.', 'Aparece sobre tu cabeza al saludar (1). Hasta 20 caracteres.', 'अभिवादन (1) गर्दा टाउकोमाथि देखिन्छ। बढीमा २० अक्षर।', 'Huonekana juu ya kichwa unaposalimia (1). Hadi herufi 20.'],
    ['처음 인사로', 'Reset', '最初に戻す', '恢复默认', 'Zurücksetzen', 'Réinitialiser', 'Ripristina', 'Restablecer', 'सुरुकै', 'Rudisha'],
    ['저장', 'Save', '保存', '保存', 'Speichern', 'Enregistrer', 'Salva', 'Guardar', 'सेभ गर्नुहोस्', 'Hifadhi'],
    ['인삿말을 저장했어요', 'Greetings saved', 'あいさつを保存しました', '问候语已保存', 'Grüße gespeichert', 'Salutations enregistrées', 'Saluti salvati', 'Saludos guardados', 'अभिवादन सेभ भयो', 'Salamu zimehifadhiwa'],
    ['고운 말로 바꿔 주세요', 'Please choose kinder words', 'やさしい言葉にしてください', '请换成友善的话', 'Bitte freundlichere Worte wählen', 'Choisissez des mots plus doux', 'Usa parole più gentili', 'Elige palabras más amables', 'राम्रा शब्द प्रयोग गर्नुहोस्', 'Tafadhali tumia maneno mazuri'],
    # 방명록
    ['📝 방명록', '📝 Guestbook', '📝 芳名録', '📝 留言板', '📝 Gästebuch', '📝 Livre d’or', '📝 Libro ospiti', '📝 Libro de visitas', '📝 अतिथि पुस्तिका', '📝 Kitabu cha wageni'],
    ['📝 정상 방명록', '📝 Summit guestbook', '📝 山頂の芳名録', '📝 山顶留言板', '📝 Gipfelbuch', '📝 Livre d’or du sommet', '📝 Libro di vetta', '📝 Libro de cumbre', '📝 शिखर अतिथि पुस्तिका', '📝 Kitabu cha kileleni'],
    ['방명록', 'Guestbook', '芳名録', '留言板', 'Gästebuch', 'Livre d’or', 'Libro ospiti', 'Libro de visitas', 'अतिथि पुस्तिका', 'Kitabu cha wageni'],
    ['정상 방명록', 'Summit guestbook', '山頂の芳名録', '山顶留言板', 'Gipfelbuch', 'Livre d’or du sommet', 'Libro di vetta', 'Libro de cumbre', 'शिखर अतिथि पुस्तिका', 'Kitabu cha kileleni'],
    ['정상에 오른 사람들이 남긴 포스트잇이에요', 'Notes left by people who reached the summit', '山頂に登った人たちが残したふせんです', '登顶的人留下的便利贴', 'Zettel von Leuten, die den Gipfel erreicht haben', 'Mots laissés par ceux qui ont atteint le sommet', 'Biglietti lasciati da chi ha raggiunto la vetta', 'Notas de quienes llegaron a la cumbre', 'शिखर पुगेकाहरूले छोडेका नोट', 'Vijikaratasi vya walioufikia kilele'],
    ['한마디 남기기 (60자)', 'Leave a note (60 characters)', 'ひとこと残す (60文字)', '留一句话 (60字)', 'Hinterlasse eine Notiz (60 Zeichen)', 'Laissez un mot (60 caractères)', 'Lascia un messaggio (60 caratteri)', 'Deja una nota (60 caracteres)', 'एउटा कुरा लेख्नुहोस् (६० अक्षर)', 'Acha ujumbe (herufi 60)'],
    ['붙이기', 'Stick it', '貼る', '贴上', 'Ankleben', 'Coller', 'Attacca', 'Pegar', 'टाँस्नुहोस्', 'Bandika'],
    ['고쳐 붙이기', 'Update note', '貼り直す', '重新贴上', 'Notiz ändern', 'Modifier le mot', 'Aggiorna', 'Actualizar nota', 'नोट फेर्नुहोस्', 'Badilisha'],
    ['떼기', 'Remove', 'はがす', '撕下', 'Abnehmen', 'Retirer', 'Togli', 'Quitar', 'हटाउनुहोस्', 'Ondoa'],
    ['내 포스트잇', 'My note', '自分のふせん', '我的便利贴', 'Meine Notiz', 'Mon mot', 'Il mio biglietto', 'Mi nota', 'मेरो नोट', 'Kikaratasi changu'],
    ['포스트잇을 붙였어요', 'Your note is up', 'ふせんを貼りました', '便利贴已贴上', 'Deine Notiz hängt', 'Votre mot est affiché', 'Biglietto attaccato', 'Nota pegada', 'नोट टाँसियो', 'Kikaratasi kimebandikwa'],
    ['포스트잇을 뗐어요', 'Note removed', 'ふせんをはがしました', '便利贴已撕下', 'Notiz entfernt', 'Mot retiré', 'Biglietto tolto', 'Nota quitada', 'नोट हटाइयो', 'Kikaratasi kimeondolewa'],
    ['아직 붙은 포스트잇이 없어요. 첫 장을 붙여 보세요.', 'No notes yet. Be the first to leave one.', 'まだふせんはありません。最初の一枚をどうぞ。', '还没有便利贴，来贴第一张吧。', 'Noch keine Notizen. Hinterlasse die erste.', 'Pas encore de mots. Laissez le premier.', 'Ancora nessun biglietto. Lascia il primo.', 'Aún no hay notas. Deja la primera.', 'अहिलेसम्म नोट छैन। पहिलो टाँस्नुहोस्।', 'Bado hakuna vikaratasi. Kuwa wa kwanza.'],
    ['정상에 오르면 포스트잇을 붙일 수 있어요', 'You can leave a note once you reach the summit', '山頂に着くとふせんを貼れます', '登顶后就能贴便利贴', 'Am Gipfel kannst du eine Notiz hinterlassen', 'Vous pourrez laisser un mot au sommet', 'Potrai lasciare un biglietto in vetta', 'Podrás dejar una nota en la cumbre', 'शिखरमा पुगेपछि नोट टाँस्न सकिन्छ', 'Ukifika kileleni unaweza kuacha kikaratasi'],
    ['방명록을 준비하고 있어요. 곧 열려요.', 'The guestbook is being set up. Opening soon.', '芳名録を準備中です。もうすぐ開きます。', '留言板正在准备中，即将开放。', 'Das Gipfelbuch wird vorbereitet.', 'Le livre d’or arrive bientôt.', 'Il libro ospiti arriva presto.', 'El libro de visitas estará listo pronto.', 'अतिथि पुस्तिका तयारी हुँदैछ।', 'Kitabu cha wageni kinaandaliwa.'],
    ['정상 방명록에 한마디 남겨 보세요', 'Leave a note in the summit guestbook', '山頂の芳名録にひとこと残しましょう', '在山顶留言板上留句话吧', 'Hinterlasse eine Notiz im Gipfelbuch', 'Laissez un mot dans le livre d’or', 'Lascia un messaggio nel libro di vetta', 'Deja una nota en el libro de cumbre', 'शिखर अतिथि पुस्तिकामा एउटा कुरा लेख्नुहोस्', 'Acha ujumbe kwenye kitabu cha kileleni'],
    ['구글로 로그인', 'Sign in with Google', 'Google でログイン', '使用 Google 登录', 'Mit Google anmelden', 'Se connecter avec Google', 'Accedi con Google', 'Iniciar sesión con Google', 'Google बाट लगइन', 'Ingia kwa Google'],
    ['산마다 한 사람 한 장 · 다시 쓰면 바뀌어요', 'One note per person per mountain · writing again replaces it', '山ごとに一人一枚・書き直すと替わります', '每座山每人一张 · 再写会替换', 'Eine Notiz pro Person und Berg · neu schreiben ersetzt sie', 'Un mot par personne et par montagne · réécrire le remplace', 'Un biglietto a persona per montagna · riscrivendo lo sostituisci', 'Una nota por persona y montaña · al reescribir se reemplaza', 'हिमालपिच्छे एक जनाको एउटा · फेरि लेखे फेरिन्छ', 'Kimoja kwa kila mtu kwa kila mlima · ukiandika tena kinabadilika'],
    # 2026-11-11 산악회·채팅 3가지
    ["님이 산악회에 초대했어요", "invited you to their hiking club", "さんが山岳会に招待しました", "邀请你加入登山队", "hat dich in den Wanderclub eingeladen", "vous invite dans son club de randonnée", "ti ha invitato nel suo gruppo", "te invitó a su club de montaña", "ले हाइकिङ क्लबमा निम्तो दिनुभयो", "amekualika kwenye klabu ya kupanda mlima"],
    ["리더를 따라 걸을까요?", "Follow the leader?", "リーダーについて歩きますか?", "要跟着队长走吗？", "Dem Leiter folgen?", "Suivre le guide ?", "Seguire il capogruppo?", "¿Seguir al líder?", "नेतालाई पछ्याउने?", "Mfuate kiongozi?"],
    ["👣 따라 걷기", "👣 Follow", "👣 ついて歩く", "👣 跟着走", "👣 Folgen", "👣 Suivre", "👣 Segui", "👣 Seguir", "👣 पछ्याउनुहोस्", "👣 Fuata"],
    ["산악회가 가득 찼어요 (최대 10명)", "The club is full (up to 10)", "山岳会がいっぱいです (最大10人)", "登山队已满 (最多10人)", "Der Club ist voll (max. 10)", "Le club est complet (10 max.)", "Il gruppo è pieno (max 10)", "El club está lleno (máx. 10)", "क्लब भरियो (बढीमा १०)", "Klabu imejaa (hadi 10)"],
    ["초대코드로 산악회를 만들었어요", "is your new club’s invite code", "の招待コードで山岳会を作りました", "是新登山队的邀请码", "ist der Einladungscode deines neuen Clubs", "est le code d’invitation de votre club", "è il codice invito del tuo gruppo", "es el código de invitación de tu club", "तपाईंको नयाँ क्लबको निम्तो कोड हो", "ni msimbo wa mwaliko wa klabu yako"],
    ["산악회를 나왔어요", "You left the club", "山岳会を抜けました", "已退出登山队", "Du hast den Club verlassen", "Vous avez quitté le club", "Hai lasciato il gruppo", "Has dejado el club", "तपाईंले क्लब छोड्नुभयो", "Umeondoka kwenye klabu"],
    ["초대코드 6자리를 넣어 주세요", "Enter the 6-character invite code", "6桁の招待コードを入れてください", "请输入6位邀请码", "Gib den 6-stelligen Einladungscode ein", "Entrez le code d’invitation à 6 caractères", "Inserisci il codice invito di 6 caratteri", "Escribe el código de 6 caracteres", "६ अक्षरको निम्तो कोड लेख्नुहोस्", "Weka msimbo wa mwaliko wa herufi 6"],
    ["이미 이 산악회에 있어요", "You’re already in this club", "もうこの山岳会にいます", "你已在这个登山队中", "Du bist schon in diesem Club", "Vous êtes déjà dans ce club", "Sei già in questo gruppo", "Ya estás en este club", "तपाईं पहिल्यै यो क्लबमा हुनुहुन्छ", "Tayari uko kwenye klabu hii"],
    ["산악회를 찾고 있어요…", "Looking for the club…", "山岳会を探しています…", "正在寻找登山队…", "Club wird gesucht…", "Recherche du club…", "Cerco il gruppo…", "Buscando el club…", "क्लब खोज्दै…", "Inatafuta klabu…"],
    ["님의 산악회에 들어왔어요", "— you joined this leader’s club", "さんの山岳会に入りました", "的登山队，你已加入", "— du bist dem Club beigetreten", "— vous avez rejoint ce club", "— sei entrato nel gruppo", "— te uniste a su club", "को क्लबमा सामेल हुनुभयो", "— umejiunga na klabu yake"],
    ["리더를 따라 걸어요", "Following the leader", "リーダーについて歩きます", "跟着队长走", "Du folgst dem Leiter", "Vous suivez le guide", "Segui il capogruppo", "Sigues al líder", "नेतालाई पछ्याउँदै", "Unamfuata kiongozi"],
    ["이 산에서 그 산악회를 찾지 못했어요", "Couldn’t find that club on this mountain", "この山でその山岳会が見つかりません", "在这座山上没有找到这个登山队", "Dieser Club ist nicht auf diesem Berg", "Ce club n’est pas sur cette montagne", "Gruppo non trovato su questa montagna", "No encontramos ese club en esta montaña", "यो हिमालमा त्यो क्लब भेटिएन", "Klabu hiyo haipo kwenye mlima huu"],
    ["리더와 같은 산에 있어야 해요", "You need to be on the same mountain as the leader", "リーダーと同じ山にいる必要があります", "需要和队长在同一座山上", "Du musst auf demselben Berg sein wie der Leiter", "Vous devez être sur la même montagne que le guide", "Devi essere sulla stessa montagna del capogruppo", "Debes estar en la misma montaña que el líder", "नेताकै हिमालमा हुनुपर्छ", "Lazima uwe mlima mmoja na kiongozi"],
    ["내가 리더예요", "I’m the leader", "私がリーダーです", "我是队长", "Ich bin der Leiter", "Je suis le guide", "Sono io il capogruppo", "Soy el líder", "म नेता हुँ", "Mimi ndiye kiongozi"],
    ["산악회원들이 나를 따라 걸어요", "Club members follow you", "メンバーが私について歩きます", "队员们跟着我走", "Die Mitglieder folgen dir", "Les membres vous suivent", "I membri ti seguono", "Los miembros te siguen", "सदस्यहरू मलाई पछ्याउँछन्", "Wanachama wanakufuata"],
    ["따라 걸을 리더가 없어요", "There’s no leader to follow", "ついて歩くリーダーがいません", "没有可以跟随的队长", "Kein Leiter zum Folgen da", "Aucun guide à suivre", "Nessun capogruppo da seguire", "No hay líder a quien seguir", "पछ्याउने नेता छैन", "Hakuna kiongozi wa kufuata"],
    ["직접 움직이면 멈춰요", "move yourself to stop", "自分で動くと止まります", "自己移动即可停止", "selbst bewegen zum Stoppen", "bougez pour arrêter", "muoviti per fermarti", "muévete para parar", "आफैँ चले रोकिन्छ", "jisogeze kusimama"],
    ["능선 산악회에 함께 가요! 초대코드", "Join my hiking club on Neungseon! Invite code", "能線の山岳会に一緒に行こう！招待コード", "一起来能线登山队吧！邀请码", "Komm in meinen Wanderclub auf Neungseon! Code", "Rejoignez mon club sur Neungseon ! Code", "Unisciti al mio gruppo su Neungseon! Codice", "¡Únete a mi club en Neungseon! Código", "Neungseon मा मेरो क्लबमा आउनुहोस्! कोड", "Jiunge na klabu yangu Neungseon! Msimbo"],
    ["초대코드와 주소를 복사했어요", "Invite code and link copied", "招待コードとリンクをコピーしました", "已复制邀请码和链接", "Code und Link kopiert", "Code et lien copiés", "Codice e link copiati", "Código y enlace copiados", "कोड र लिङ्क कपी भयो", "Msimbo na kiungo vimenakiliwa"],
    ["이제 내가 리더예요", "You’re the leader now", "今は私がリーダーです", "现在我是队长", "Jetzt bist du der Leiter", "Vous êtes maintenant le guide", "Ora sei tu il capogruppo", "Ahora eres el líder", "अब तपाईं नेता हुनुहुन्छ", "Sasa wewe ni kiongozi"],
    ["따라 걷기를 멈췄어요", "Stopped following", "ついて歩くのをやめました", "已停止跟随", "Folgen beendet", "Vous ne suivez plus", "Hai smesso di seguire", "Dejaste de seguir", "पछ्याउन रोकियो", "Umeacha kufuata"],
    ["리더", "Leader", "リーダー", "队长", "Leiter", "Guide", "Capogruppo", "Líder", "नेता", "Kiongozi"],
    ["따라 걷는 중", "Following", "ついて歩き中", "跟随中", "Folgt", "Suit", "Segue", "Siguiendo", "पछ्याउँदै", "Anafuata"],
    ["다른 산악회", "Another club", "別の山岳会", "其他登山队", "Anderer Club", "Autre club", "Altro gruppo", "Otro club", "अर्को क्लब", "Klabu nyingine"],
    ["💬 귓속말 보내기", "💬 Whisper", "💬 ささやく", "💬 发送悄悄话", "💬 Flüstern", "💬 Chuchoter", "💬 Sussurra", "💬 Susurrar", "💬 कानेखुसी", "💬 Nong’ona"],
    ["(나)", "(me)", "(自分)", "(我)", "(ich)", "(moi)", "(io)", "(yo)", "(म)", "(mimi)"],
    ["따라 걷기 멈추기", "Stop following", "ついて歩くのをやめる", "停止跟随", "Nicht mehr folgen", "Arrêter de suivre", "Smetti di seguire", "Dejar de seguir", "पछ्याउन रोक्नुहोस्", "Acha kufuata"],
    ["👣 리더 따라 걷기", "👣 Follow the leader", "👣 リーダーについて歩く", "👣 跟着队长走", "👣 Dem Leiter folgen", "👣 Suivre le guide", "👣 Segui il capogruppo", "👣 Seguir al líder", "👣 नेतालाई पछ्याउनुहोस्", "👣 Mfuate kiongozi"],
    ["산악회원들이 줄지어 따라와요", "Members follow you in a line", "メンバーが列になってついてきます", "队员们排成一列跟着你", "Die Mitglieder folgen dir in einer Reihe", "Les membres vous suivent en file", "I membri ti seguono in fila", "Los miembros te siguen en fila", "सदस्यहरू लाइन लागेर पछ्याउँछन्", "Wanachama wanakufuata kwa mstari"],
    ["초대코드를 알려 주면 최대 10명까지 함께 걸을 수 있어요", "Share the invite code to hike with up to 10 people", "招待コードを教えると最大10人で一緒に歩けます", "分享邀请码，最多10人一起走", "Teile den Code und wandere mit bis zu 10 Leuten", "Partagez le code pour marcher jusqu’à 10", "Condividi il codice e cammina con fino a 10 persone", "Comparte el código y camina con hasta 10 personas", "कोड बाँडेर बढीमा १० जनासँग हिँड्नुहोस्", "Shiriki msimbo mtembee hadi watu 10"],
    ["리더를 따라 걸으면 같은 보폭으로 줄지어 걸어요", "Follow the leader to walk in a line at the same pace", "リーダーについて歩くと同じ歩幅で列になって歩きます", "跟着队长走，就会以相同步伐排队前进", "Folge dem Leiter und geht im gleichen Schritt in einer Reihe", "Suivez le guide pour marcher en file au même pas", "Segui il capogruppo per camminare in fila allo stesso passo", "Sigue al líder para caminar en fila al mismo paso", "नेतालाई पछ्याए एउटै गतिमा लाइन लागेर हिँडिन्छ", "Mfuate kiongozi mtembee kwa mstari kwa mwendo mmoja"],
    ["리더가 산을 떠나 이제 내가 산악회 리더예요", "The leader left, so you’re the club leader now", "リーダーが山を離れたので、今は私がリーダーです", "队长离开了，现在你是队长", "Der Leiter ist gegangen – jetzt leitest du den Club", "Le guide est parti : vous êtes le nouveau guide", "Il capogruppo è andato via: ora guidi tu", "El líder se fue: ahora tú eres el líder", "नेता गएकाले अब तपाईं क्लबको नेता हुनुहुन्छ", "Kiongozi ameondoka, sasa wewe ni kiongozi"],
    ["님이 새 리더가 됐어요", "is the new leader", "さんが新しいリーダーになりました", "成为新队长", "ist der neue Leiter", "est le nouveau guide", "è il nuovo capogruppo", "es el nuevo líder", "नयाँ नेता हुनुभयो", "ndiye kiongozi mpya"],
    ["산악회원과 멀어졌어요", "You’re far from your club", "メンバーと離れました", "和队员离远了", "Du bist weit von deinem Club entfernt", "Vous êtes loin de votre club", "Sei lontano dal gruppo", "Estás lejos de tu club", "क्लबबाट टाढा हुनुभयो", "Uko mbali na klabu yako"],
    ["잠시 기다려 볼까요?", "wait a moment?", "少し待ちましょうか?", "要等一等吗？", "kurz warten?", "on attend un peu ?", "aspetti un attimo?", "¿esperas un poco?", "अलि पर्खने?", "subiri kidogo?"],
    ["함께하던 산악회원이 모두 산을 떠났어요", "All your club members left the mountain", "一緒にいたメンバーが全員山を離れました", "队员们都离开了这座山", "Alle Mitglieder haben den Berg verlassen", "Tous les membres ont quitté la montagne", "Tutti i membri hanno lasciato la montagna", "Todos los miembros dejaron la montaña", "सबै सदस्यले हिमाल छोडे", "Wanachama wote wameondoka mlimani"],
    ["리더를 따라 걷는 중", "following the leader", "リーダーについて歩き中", "正在跟随队长", "folgt dem Leiter", "suit le guide", "segue il capogruppo", "siguiendo al líder", "नेतालाई पछ्याउँदै", "anamfuata kiongozi"],
    ["멈추기", "Stop", "止める", "停止", "Stopp", "Arrêter", "Ferma", "Parar", "रोक्नुहोस्", "Simama"],
    ["산악회를 만들거나 초대코드로 들어가 최대 10명이 함께 걸어요. 리더를 따라 걸으면 같은 보폭으로 줄지어 걸어요.", "Create a club or join with an invite code — up to 10 people. Follow the leader to walk in a line at the same pace.", "山岳会を作るか招待コードで入って、最大10人で一緒に歩きます。リーダーについて歩くと同じ歩幅で列になって歩きます。", "创建登山队或用邀请码加入，最多10人同行。跟着队长走就会以相同步伐排队前进。", "Gründe einen Club oder tritt mit einem Code bei – bis zu 10 Leute. Folge dem Leiter, um im gleichen Schritt in einer Reihe zu gehen.", "Créez un club ou rejoignez-en un avec un code — jusqu’à 10 personnes. Suivez le guide pour marcher en file au même pas.", "Crea un gruppo o entra con un codice — fino a 10 persone. Segui il capogruppo per camminare in fila allo stesso passo.", "Crea un club o únete con un código — hasta 10 personas. Sigue al líder para caminar en fila al mismo paso.", "क्लब बनाउनुहोस् वा कोडले सामेल हुनुहोस् — बढीमा १० जना। नेतालाई पछ्याए एउटै गतिमा लाइन लागेर हिँडिन्छ।", "Unda klabu au jiunge kwa msimbo — hadi watu 10. Mfuate kiongozi mtembee kwa mstari kwa mwendo mmoja."],
    ["⛰ 산악회", "⛰ Hiking club", "⛰ 山岳会", "⛰ 登山队", "⛰ Wanderclub", "⛰ Club de randonnée", "⛰ Gruppo", "⛰ Club de montaña", "⛰ हाइकिङ क्लब", "⛰ Klabu ya kupanda"],
    ["초대코드", "Invite code", "招待コード", "邀请码", "Einladungscode", "Code d’invitation", "Codice invito", "Código de invitación", "निम्तो कोड", "Msimbo wa mwaliko"],
    ["초대하기", "Invite", "招待する", "邀请", "Einladen", "Inviter", "Invita", "Invitar", "निम्तो दिनुहोस्", "Alika"],
    ["산악회 나가기", "Leave the club", "山岳会を抜ける", "退出登山队", "Club verlassen", "Quitter le club", "Lascia il gruppo", "Salir del club", "क्लब छोड्नुहोस्", "Ondoka kwenye klabu"],
    ["⛰ 산악회 만들기", "⛰ Create a club", "⛰ 山岳会を作る", "⛰ 创建登山队", "⛰ Club gründen", "⛰ Créer un club", "⛰ Crea un gruppo", "⛰ Crear un club", "⛰ क्लब बनाउनुहोस्", "⛰ Unda klabu"],
    ["초대코드 6자리", "6-character invite code", "6桁の招待コード", "6位邀请码", "6-stelliger Code", "Code à 6 caractères", "Codice di 6 caratteri", "Código de 6 caracteres", "६ अक्षरको कोड", "Msimbo wa herufi 6"],
    ["들어가기", "Join", "入る", "加入", "Beitreten", "Rejoindre", "Entra", "Unirse", "सामेल हुनुहोस्", "Jiunge"],
    ["이 산에 있는 사람", "People on this mountain", "この山にいる人", "这座山上的人", "Leute auf diesem Berg", "Personnes sur cette montagne", "Persone su questa montagna", "Gente en esta montaña", "यो हिमालमा भएका मानिस", "Watu walio kwenye mlima huu"],
    ["전체", "All", "全体", "全部", "Alle", "Tous", "Tutti", "Todos", "सबै", "Wote"],
    ["산악회", "Club", "山岳会", "登山队", "Club", "Club", "Gruppo", "Club", "क्लब", "Klabu"],
    ["귓속말", "Whisper", "ささやき", "悄悄话", "Flüstern", "Chuchoter", "Sussurro", "Susurro", "कानेखुसी", "Nong’ona"],
    ["끄기", "Off", "オフ", "关闭", "Aus", "Désactiver", "Spegni", "Apagar", "बन्द", "Zima"],
    ["켜기", "On", "オン", "开启", "An", "Activer", "Accendi", "Encender", "खोल्नुहोस्", "Washa"],
    ["채팅 켜기/끄기", "Turn chat on/off", "チャットのオン/オフ", "开关聊天", "Chat an/aus", "Activer/désactiver le chat", "Attiva/disattiva chat", "Activar/desactivar chat", "च्याट खोल्ने/बन्द गर्ने", "Washa/zima gumzo"],
    ["채팅이 꺼져 있어요. 다른 사람의 말풍선과 채팅 알림이 보이지 않아요.", "Chat is off. Other people’s speech bubbles and chat alerts are hidden.", "チャットはオフです。ほかの人の吹き出しと通知は表示されません。", "聊天已关闭。不会显示他人的气泡和聊天提醒。", "Der Chat ist aus. Sprechblasen und Chat-Hinweise sind ausgeblendet.", "Le chat est désactivé. Les bulles et alertes sont masquées.", "La chat è spenta. Fumetti e avvisi sono nascosti.", "El chat está apagado. Se ocultan burbujas y avisos.", "च्याट बन्द छ। अरूका बबल र सूचना देखिँदैनन्।", "Gumzo limezimwa. Viputo na arifa hazionekani."],
    ["채팅 켜기", "Turn chat on", "チャットをオンにする", "开启聊天", "Chat einschalten", "Activer le chat", "Accendi la chat", "Activar el chat", "च्याट खोल्नुहोस्", "Washa gumzo"],
    ["귓속말 받는 사람", "Whisper to", "ささやく相手", "悄悄话对象", "Flüstern an", "Chuchoter à", "Sussurra a", "Susurrar a", "कानेखुसी पाउने", "Nong’ona kwa"],
    ["바꾸기", "Change", "変える", "更换", "Ändern", "Changer", "Cambia", "Cambiar", "फेर्नुहोस्", "Badilisha"],
    ["받는 사람 바꾸기", "Change recipient", "相手を変える", "更换对象", "Empfänger ändern", "Changer de destinataire", "Cambia destinatario", "Cambiar destinatario", "पाउने फेर्नुहोस्", "Badilisha mpokeaji"],
    ["이모티콘", "Emoji", "絵文字", "表情", "Emoji", "Émoji", "Emoji", "Emoji", "इमोजी", "Emoji"],
    ["채팅을 껐어요", "Chat turned off", "チャットをオフにしました", "已关闭聊天", "Chat ausgeschaltet", "Chat désactivé", "Chat spenta", "Chat apagado", "च्याट बन्द गरियो", "Gumzo limezimwa"],
    ["말풍선과 알림이 보이지 않아요", "bubbles and alerts are hidden", "吹き出しと通知は表示されません", "气泡和提醒不会显示", "Sprechblasen und Hinweise sind aus", "bulles et alertes masquées", "fumetti e avvisi nascosti", "burbujas y avisos ocultos", "बबल र सूचना देखिँदैनन्", "viputo na arifa vimefichwa"],
    ["채팅을 켰어요", "Chat turned on", "チャットをオンにしました", "已开启聊天", "Chat eingeschaltet", "Chat activé", "Chat accesa", "Chat activado", "च्याट खोलियो", "Gumzo limewashwa"],
    ["산악회원에게만 보여요", "Only club members see this", "山岳会のメンバーだけに見えます", "仅队员可见", "Nur Clubmitglieder sehen das", "Visible seulement par le club", "Lo vedono solo i membri", "Solo lo ven los miembros", "क्लब सदस्यले मात्र देख्छन्", "Wanachama pekee wanaona"],
    ["귓속말은 이 사람에게만 보여요", "Only this person sees your whisper", "ささやきはこの人だけに見えます", "悄悄话只有对方能看到", "Nur diese Person sieht dein Flüstern", "Seule cette personne voit le message", "Solo questa persona vede il sussurro", "Solo esta persona ve el susurro", "कानेखुसी यो व्यक्तिले मात्र देख्छ", "Ni mtu huyu tu anayeona"],
    ["산악회에 들어가면 산악회원끼리 이야기할 수 있어요", "Join a club to chat with its members", "山岳会に入るとメンバー同士で話せます", "加入登山队后可以和队员聊天", "Tritt einem Club bei, um mit den Mitgliedern zu chatten", "Rejoignez un club pour discuter entre membres", "Entra in un gruppo per parlare con i membri", "Únete a un club para hablar con sus miembros", "क्लबमा सामेल भएपछि सदस्यसँग कुरा गर्न सकिन्छ", "Jiunge na klabu ili uzungumze na wanachama"],
    ["⛰ 산악회 만들기·들어가기", "⛰ Create or join a club", "⛰ 山岳会を作る・入る", "⛰ 创建或加入登山队", "⛰ Club gründen oder beitreten", "⛰ Créer ou rejoindre un club", "⛰ Crea o entra in un gruppo", "⛰ Crear o unirse a un club", "⛰ क्लब बनाउनुहोस् वा सामेल हुनुहोस्", "⛰ Unda au jiunge na klabu"],
    ["누구에게 귓속말을 보낼까요?", "Who do you want to whisper to?", "誰にささやきますか?", "要给谁发悄悄话？", "Wem möchtest du flüstern?", "À qui voulez-vous chuchoter ?", "A chi vuoi sussurrare?", "¿A quién quieres susurrar?", "कसलाई कानेखुसी गर्ने?", "Unataka kumnong’oneza nani?"],
    ["지금은 귓속말을 보낼 사람이 없어요", "There’s no one to whisper to right now", "今はささやく相手がいません", "现在没有可以发悄悄话的人", "Gerade ist niemand zum Flüstern da", "Personne à qui chuchoter pour l’instant", "Nessuno a cui sussurrare ora", "No hay nadie a quien susurrar ahora", "अहिले कानेखुसी गर्ने कोही छैन", "Hakuna wa kumnong’oneza sasa"],
    ["귓속말은 받는 사람과 나만 볼 수 있어요", "Only you and the recipient can see whispers", "ささやきは相手と自分だけが見られます", "悄悄话只有你和对方能看到", "Nur du und der Empfänger seht das", "Seuls vous et le destinataire voyez ces messages", "Solo tu e il destinatario potete vederli", "Solo tú y el destinatario pueden verlos", "कानेखुसी तपाईं र पाउनेले मात्र देख्छन्", "Ni wewe na mpokeaji tu mnaoona"],
    ["산악회원끼리만 보이는 이야기예요", "Only club members can see this chat", "山岳会のメンバーだけに見える会話です", "只有队员能看到的聊天", "Nur Clubmitglieder sehen diesen Chat", "Seuls les membres voient cette discussion", "Solo i membri vedono questa chat", "Solo los miembros ven este chat", "क्लब सदस्यले मात्र देख्ने कुराकानी", "Wanachama pekee wanaona mazungumzo haya"],
    ["아직 준비 중이에요", "Not ready yet", "まだ準備中です", "还在准备中", "Noch nicht bereit", "Pas encore prêt", "Non ancora pronto", "Aún no está listo", "अझै तयारी हुँदैछ", "Bado haijawa tayari"],
    ["곧 열려요", "opening soon", "もうすぐ開きます", "即将开放", "bald verfügbar", "bientôt disponible", "in arrivo", "pronto", "छिट्टै खुल्छ", "itafunguliwa hivi karibuni"],
    ["님의 귓속말이 왔어요 💬", "whispered to you 💬", "さんからささやきが届きました 💬", "给你发了悄悄话 💬", "hat dir etwas zugeflüstert 💬", "vous a chuchoté 💬", "ti ha sussurrato 💬", "te susurró 💬", "ले कानेखुसी गर्नुभयो 💬", "amekunong’oneza 💬"],
    ["지우기", "Delete", "消す", "删除", "Löschen", "Supprimer", "Elimina", "Borrar", "मेटाउनुहोस्", "Futa"],
    ["더 보기", "More", "もっと", "更多", "Mehr", "Plus", "Altro", "Más", "थप", "Zaidi"],
]

SOCIAL_CSS = r'''
/* ---------- 함께가기·채팅·방명록 (pipeline/social_patch.py) ---------- */
#soBar{left:max(14px,env(safe-area-inset-left,0px));top:50%;transform:translateY(-50%);display:none;flex-direction:column;gap:8px;z-index:3}
body.soOn #soBar{display:flex}
#soBar button{pointer-events:auto;position:relative;width:46px;height:46px;border-radius:50%;display:grid;place-items:center;color:#fff;cursor:pointer;padding:0}
#soBar button svg{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}
#soBar button.on{background:rgba(63,138,85,.75)}
#soBar .bd{position:absolute;top:-3px;right:-3px;min-width:18px;height:18px;border-radius:9px;background:#d9542b;color:#fff;font-size:11px;font-weight:800;line-height:18px;text-align:center;padding:0 4px;box-sizing:border-box}
#soBar .bd[hidden]{display:none}
body.camping #soBar,body.photo #soBar{display:none!important}
#soChat{position:fixed;z-index:20;left:calc(max(14px,env(safe-area-inset-left,0px)) + 56px);top:50%;transform:translateY(-50%);width:min(360px,80vw);height:min(420px,64vh);border-radius:18px;display:flex;flex-direction:column;color:#fff;pointer-events:auto;overflow:hidden}
#soChat[hidden]{display:none}
.soHead{display:flex;align-items:center;gap:6px;padding:8px 8px 7px 12px;border-bottom:1px solid var(--line)}
.soHead b{font-size:14px}.soHead span{flex:1;font-size:11.5px;opacity:.75;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.soX{border:0;background:rgba(255,255,255,.12);color:inherit;width:28px;height:28px;border-radius:50%;cursor:pointer;font-size:13px;flex:none}
#soMsgs{flex:1;overflow-y:auto;padding:8px 12px;display:flex;flex-direction:column;gap:5px;font-size:13.5px;line-height:1.4;overscroll-behavior:contain}
#soMsgs .m{cursor:pointer;border-radius:8px;padding:2px 4px;margin:0 -4px;word-break:break-word}
#soMsgs .m:hover{background:rgba(255,255,255,.08)}
#soMsgs .m b{font-weight:700;margin-right:6px}
#soMsgs .m.me b{color:#ffd9a6}
#soMsgs .m small{opacity:.55;font-size:10.5px;margin-left:6px}
#soMsgs .empty{opacity:.7;font-size:12.5px;text-align:center;margin:auto 0}
#soChatF{display:flex;gap:6px;padding:8px;border-top:1px solid var(--line)}
#soChatF input{flex:1;min-width:0;font:inherit;font-size:16px;padding:8px 12px;border-radius:12px;border:1px solid rgba(255,255,255,.25);background:rgba(255,255,255,.92);color:#2a2219}
#soChatF button,#soChatLogin button{border:0;border-radius:12px;padding:0 14px;font-weight:700;background:var(--maple,#c8562a);color:#fff;cursor:pointer;font-size:14px}
#soChatLogin{padding:10px;display:flex;gap:8px;align-items:center;justify-content:space-between;font-size:12.5px;border-top:1px solid var(--line)}
#soChatLogin[hidden],#soChatF[hidden]{display:none}#soChatLogin button{padding:8px 12px}
#soMenu{position:fixed;z-index:30;display:flex;flex-direction:column;gap:2px;padding:6px;border-radius:14px;color:#fff;pointer-events:auto}
#soMenu[hidden]{display:none}
#soMenu button{border:0;background:transparent;color:inherit;text-align:left;padding:8px 12px;border-radius:10px;font-size:13.5px;cursor:pointer;white-space:nowrap}
#soMenu button:hover{background:rgba(255,255,255,.12)}
#soInv{position:fixed;z-index:22;left:50%;top:calc(130px + env(safe-area-inset-top,0px));transform:translateX(-50%);border-radius:18px;padding:12px 14px;display:flex;flex-direction:column;gap:10px;color:#fff;pointer-events:auto;min-width:260px;max-width:92vw;text-align:center}
#soInv[hidden]{display:none}
#soInv .t{font-size:15px}#soInv .t b{margin-right:2px}
#soInv .b{display:flex;gap:8px;justify-content:center}
#soInv button,#soChip button{border:0;border-radius:999px;padding:8px 16px;font-weight:700;font-size:14px;cursor:pointer}
#soInvY,#soChipB{background:linear-gradient(135deg,#3f8a55,#5aa66d);color:#fff}
#soInvN2{background:rgba(255,255,255,.16);color:#fff}
#soChip{position:fixed;z-index:21;left:50%;top:calc(130px + env(safe-area-inset-top,0px));transform:translateX(-50%);display:flex;align-items:center;gap:10px;padding:6px 6px 6px 16px;color:#fff;pointer-events:auto;font-size:13.5px;max-width:92vw}
#soChip[hidden]{display:none}#soChip .x{background:transparent;color:#fff;opacity:.7;padding:6px 8px}
#soNote{position:fixed;z-index:21;left:50%;top:calc(96px + env(safe-area-inset-top,0px));transform:translateX(-50%);padding:9px 18px;font-size:14px;color:#fff;max-width:90vw;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;pointer-events:none}
#soNote[hidden]{display:none}#soNote b{margin-right:3px}
.soCard{max-width:440px!important}
.soCard h1{font-size:24px!important;margin:0 0 6px}
.soRow{display:flex;align-items:center;gap:10px;padding:9px 4px;border-bottom:1px solid var(--paperLine)}
.soRow i{width:12px;height:12px;border-radius:50%;flex:none}
.soRow .nm{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:600}
.soRow small{opacity:.6;font-size:12px;white-space:nowrap}
.soRow button,.soPartyB button{border:1.5px solid var(--paperLine);background:#fff;color:var(--ink);border-radius:999px;padding:7px 12px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap}
.soRow button.go{background:#3f8a55;border-color:#3f8a55;color:#fff}
.soRow .tagd{font-size:12px;font-weight:700;color:#3f8a55;white-space:nowrap}
.soRow.hi{background:rgba(227,176,79,.18);border-radius:10px}
#soClub{margin:10px 0 4px;padding:10px 12px;border-radius:14px;background:rgba(63,138,85,.1)}
#soClub[hidden],#soNoClub[hidden]{display:none}
#soClub .h{display:flex;align-items:center;gap:8px;font-size:13.5px;color:#3f8a55;flex-wrap:wrap}
#soClub .h .cnt{font-size:12px;opacity:.75;font-variant-numeric:tabular-nums}#soClub .h .sp{flex:1}
#soClub .h .code{font-size:12.5px;color:var(--ink)}#soClub .h .code b{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:16px;letter-spacing:.12em;margin-left:2px}
#soClub .h button,#soNoClub .soJoin button{border:0;border-radius:999px;padding:7px 13px;font-size:13px;font-weight:700;background:#3f8a55;color:#fff;cursor:pointer}
#soClub .hint{font-size:12px;opacity:.7;margin:4px 0 4px}
.soRow .tagl{font-size:11px;font-weight:800;color:#a8741a;background:rgba(227,176,79,.22);border-radius:999px;padding:2px 7px;white-space:nowrap}
.soRow .tagl::before{content:'👑 '}.soRow .tagd.mute{color:var(--mute,#888)}
.soRow.me{opacity:.92}.soRow.me small{opacity:.55}
#soNoClub{display:flex;flex-direction:column;gap:8px;margin:12px 0 6px}
.soBig{border:0;border-radius:14px;padding:12px;font:inherit;font-size:15px;font-weight:800;background:linear-gradient(135deg,#3f8a55,#5aa66d);color:#fff;cursor:pointer}
.soJoin{display:flex;gap:8px}.soJoin input{flex:1;min-width:0;font:inherit;font-size:16px;padding:9px 12px;border-radius:12px;border:1px solid var(--paperLine);background:#fff;color:var(--ink);text-transform:uppercase;letter-spacing:.1em;font-family:ui-monospace,Menlo,Consolas,monospace}
.soJoin button:disabled{opacity:.5}
.soCard .h2{font-size:12.5px;font-weight:700;opacity:.6;margin:14px 0 2px}
.soTabs{flex:1;display:flex;gap:2px;min-width:0}
.soTabs button{position:relative;border:0;background:transparent;color:inherit;opacity:.65;font:inherit;font-size:12.5px;font-weight:700;padding:5px 8px;border-radius:999px;cursor:pointer;white-space:nowrap}
.soTabs button.on{opacity:1;background:rgba(255,255,255,.16)}
.soTabs .tn{position:absolute;top:-4px;right:-3px;min-width:15px;height:15px;border-radius:8px;background:#d9542b;color:#fff;font-size:9.5px;font-style:normal;line-height:15px;text-align:center;padding:0 3px;box-sizing:border-box}
.soTabs .tn[hidden]{display:none}
.soOff{border:1px solid rgba(255,255,255,.3);background:transparent;color:inherit;border-radius:999px;padding:3px 9px;font:inherit;font-size:11.5px;cursor:pointer;opacity:.8;flex:none}
.soOff.off{background:#3f8a55;border-color:#3f8a55;opacity:1}
#soChatBody{flex:1;display:flex;flex-direction:column;min-height:0}#soChatBody[hidden]{display:none}
#soChatOffBox{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:12px;padding:18px;text-align:center;font-size:13px;opacity:.9}#soChatOffBox[hidden]{display:none}
#soChatOffBox p{margin:0;line-height:1.5}#soChatOffBox button,.soLink{border:0;border-radius:999px;padding:9px 18px;font:inherit;font-size:14px;font-weight:700;background:#3f8a55;color:#fff;cursor:pointer}
.soLink{align-self:center;margin-top:8px;font-size:13px;padding:8px 14px}
#soWho{display:flex;align-items:center;gap:6px;padding:6px 12px;font-size:12px;background:rgba(255,255,255,.07)}#soWho[hidden]{display:none}
#soWho span{opacity:.7}#soWho b{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:13px}
#soWho button{border:0;background:rgba(255,255,255,.14);color:inherit;border-radius:999px;padding:3px 10px;font:inherit;font-size:11.5px;cursor:pointer}
.soWhoL{display:flex;flex-wrap:wrap;gap:6px;justify-content:center;padding:6px 0}
.soWhoL button{border:1px solid rgba(255,255,255,.3);background:rgba(255,255,255,.08);color:inherit;border-radius:999px;padding:7px 13px;font:inherit;font-size:13px;cursor:pointer}
.soWhoL button.new{border-color:#e3b04f}.soWhoL button.new::after{content:' •';color:#e3b04f}
#soMsgs .m.emo{font-size:26px;line-height:1.25}#soMsgs .m.emo b,#soMsgs .m.emo small{font-size:12px}
#soEmo{display:grid;grid-template-columns:repeat(8,1fr);gap:2px;padding:6px 8px;border-top:1px solid var(--line);max-height:120px;overflow-y:auto}#soEmo[hidden]{display:none}
#soEmo button{border:0;background:transparent;font-size:21px;line-height:1;padding:5px 0;border-radius:8px;cursor:pointer}#soEmo button:hover{background:rgba(255,255,255,.12)}
#soChatF #soEmoB{background:transparent;padding:0 4px;font-size:20px;flex:none}
#soFollowPill{position:fixed;z-index:21;left:50%;top:calc(96px + env(safe-area-inset-top,0px));transform:translateX(-50%);display:flex;align-items:center;gap:10px;padding:5px 5px 5px 14px;color:#fff;pointer-events:auto;font-size:13px;max-width:92vw;white-space:nowrap}
#soFollowPill[hidden]{display:none}#soFollowPill > span{overflow:hidden;text-overflow:ellipsis}
#soFollowPill button{border:0;border-radius:999px;padding:6px 12px;font:inherit;font-size:12.5px;font-weight:700;background:rgba(255,255,255,.18);color:#fff;cursor:pointer}
body.chatOff #soChatB{opacity:.55}body.chatOff #soChatB::after{content:'';position:absolute;left:11px;right:11px;top:50%;height:2px;background:currentColor;transform:rotate(-40deg);border-radius:2px}
.tag.lead .n span::before{content:'👑 '}
.tag.lead.buddy .n span::before{content:'👑 '}
.soPartyB{display:flex;gap:8px;flex-wrap:wrap;margin-top:8px}
.soPartyB button.on{background:#3f8a55;border-color:#3f8a55;color:#fff}
#soList .empty,#soGreetL + .empty{opacity:.65;font-size:13.5px;text-align:center;padding:16px 0}
#soGreetL{display:flex;flex-direction:column;gap:8px;margin:12px 0 4px}
#soGreetL input{font:inherit;font-size:16px;padding:9px 12px;border-radius:10px;border:1px solid var(--paperLine);background:#fff;color:var(--ink)}
#soGreetL input.bad{border-color:#d9542b;background:#fff3ef}
.tag.peer .n{pointer-events:auto;cursor:pointer}
.tag.buddy .n{background:rgba(52,120,74,.82)}
.tag.buddy .n span::before{content:'🤝 '}
#soWall{max-width:640px!important;width:100%}
#soBoard{display:grid;grid-template-columns:repeat(auto-fill,minmax(130px,1fr));gap:12px;margin:12px 0;padding:14px;border-radius:14px;background:#b88b5a radial-gradient(rgba(0,0,0,.08) 1px,transparent 1.5px) 0 0/7px 7px;max-height:46vh;overflow-y:auto;min-height:120px}
#soBoard .pi{position:relative;color:#3a2e20;padding:12px 10px 8px;min-height:96px;box-shadow:0 4px 10px rgba(0,0,0,.25);display:flex;flex-direction:column;gap:6px;font-size:13.5px;line-height:1.35;word-break:break-word;cursor:pointer}
#soBoard .pi::before{content:'';position:absolute;top:-5px;left:50%;width:34px;height:12px;transform:translateX(-50%) rotate(-2deg);background:rgba(255,255,255,.55);box-shadow:0 1px 2px rgba(0,0,0,.1)}
#soBoard .pi .w{flex:1}
#soBoard .pi .by{font-size:11px;opacity:.65;display:flex;justify-content:space-between;gap:4px}
#soBoard .pi.mine{outline:2.5px solid #3f8a55;outline-offset:2px}
#soBoard .empty{grid-column:1/-1;color:#fff;text-align:center;font-size:14px;padding:24px 0;text-shadow:0 1px 3px rgba(0,0,0,.4)}
#soWrite{display:flex;flex-direction:column;gap:8px}
#soWrite[hidden]{display:none}
#soWrite .rw{display:flex;gap:8px}
#soWrite input{flex:1;min-width:0;font:inherit;font-size:16px;padding:10px 12px;border-radius:10px;border:1px solid var(--paperLine);background:#fff;color:var(--ink)}
#soWrite .cols{display:flex;gap:8px;align-items:center}
#soWrite .cols button{width:28px;height:28px;border-radius:6px;border:2px solid rgba(0,0,0,.12);cursor:pointer;padding:0}
#soWrite .cols button.on{border-color:#2a2219;transform:scale(1.12)}
#soWrite .cols small{flex:1;text-align:right;font-size:11.5px;opacity:.65}
#soWrite .btn{margin-top:0;width:auto;padding:10px 18px;font-size:15px}
#soWrite .btn.sec{margin-top:0}
#soGuestMsg{font-size:13px;opacity:.8;text-align:center;padding:6px 0}
#soGuestMsg[hidden]{display:none}
#soGuestMsg button{margin-left:8px;border:0;border-radius:999px;padding:7px 14px;background:var(--maple,#c8562a);color:#fff;font-weight:700;cursor:pointer}
#soPeople,#soGreet,#soGuest{z-index:14}
#soGuestEnd{margin-top:8px}
body.touch #soBar{gap:6px}
body.touch #soBar button{width:42px;height:42px}
@media (orientation:portrait){
  body.touch #soBar{top:auto;transform:none;bottom:calc(250px + env(safe-area-inset-bottom,0px));left:max(10px,env(safe-area-inset-left,0px))}
}
body.touch #soChat{left:8px;right:8px;width:auto;top:calc(8px + env(safe-area-inset-top,0px));transform:none;height:min(360px,calc(var(--vh,100vh) - 24px),52vh)}
body.touch.kbd #soChat{height:calc(var(--vh,100vh) - 16px);max-height:420px}
body.touch #soFollowPill{top:calc(104px + env(safe-area-inset-top,0px))}
body.touch #soInv,body.touch #soChip{top:calc(110px + env(safe-area-inset-top,0px))}
body.touch #soNote{top:calc(64px + env(safe-area-inset-top,0px));font-size:12.5px;padding:7px 14px}
body.clean #soBar,body.clean #soChat{opacity:0!important;pointer-events:none!important}
body.clean #soBar *{pointer-events:none!important}
'''

ICON_CHAT = '<svg viewBox="0 0 24 24"><path d="M4.5 5.5h15a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H10l-4.5 3.5V16.5h-1a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1z"/><path d="M8 10h8M8 13h5"/></svg>'
ICON_PEOPLE = '<svg viewBox="0 0 24 24"><circle cx="8.5" cy="8" r="3"/><circle cx="16.5" cy="9" r="2.5"/><path d="M3 19c0-3.2 2.4-5.4 5.5-5.4S14 15.8 14 19M14.5 14c2.8-.4 6 1.2 6 4.6"/></svg>'

SOCIAL_HTML = (r'''
<div id="soBar" class="hud">
  <button id="soChatB" class="glass" title="채팅 (Enter)" aria-label="채팅">''' + ICON_CHAT + r'''<i class="bd" id="soBadge" hidden></i></button>
  <button id="soPeopleB" class="glass" title="함께 가기" aria-label="함께 가기">''' + ICON_PEOPLE + r'''<i class="bd" id="soPBadge" hidden></i></button>
</div>
<div id="soChat" class="glass" hidden>
  <div class="soHead"><b>채팅</b><span class="soTabs"><button id="soTab_all" type="button">전체<i class="tn" id="soTabN_all" hidden></i></button><button id="soTab_club" type="button">산악회<i class="tn" id="soTabN_club" hidden></i></button><button id="soTab_dm" type="button">귓속말<i class="tn" id="soTabN_dm" hidden></i></button></span><button class="soOff" id="soChatOff" type="button" title="채팅 켜기/끄기" aria-label="채팅 켜기/끄기">끄기</button><button class="soX" id="soChatX" aria-label="닫기">✕</button></div>
  <div id="soChatOffBox" hidden><p>채팅이 꺼져 있어요. 다른 사람의 말풍선과 채팅 알림이 보이지 않아요.</p><button id="soChatOn" type="button">채팅 켜기</button></div>
  <div id="soChatBody">
  <div id="soWho" hidden><span>귓속말 받는 사람</span><b class="ugc" id="soWhoN"></b><button id="soWhoX" type="button" aria-label="받는 사람 바꾸기">바꾸기</button></div>
  <div id="soMsgs" class="ugc"></div>
  <div id="soEmo" hidden></div>
  <div id="soChatLogin" hidden><span>채팅은 구글로 로그인하면 쓸 수 있어요</span><button id="soChatG" type="button">구글로 로그인</button></div>
  <form id="soChatF" autocomplete="off"><button id="soEmoB" type="button" aria-label="이모티콘">😊</button><input id="soChatIn" maxlength="80" placeholder="고운 말로 인사해 보세요" enterkeyhint="send" aria-label="채팅"><button type="submit">보내기</button></form>
  </div>
</div>
<div id="soMenu" class="glass" hidden></div>
<div id="soInv" class="glass" hidden role="alertdialog"><div class="t"><b class="ugc" id="soInvName"></b> <span id="soInvT">님이 함께 가자고 해요</span></div><div class="b"><button id="soInvY">함께 가기</button><button id="soInvN2">괜찮아요</button></div></div>
<div id="soChip" class="glass pill" hidden><span><b class="ugc" id="soChipName"></b> <span id="soChipT">님이 가까이 있어요</span></span><button id="soChipB">함께 가기 제안</button><button class="x" id="soChipX" aria-label="닫기">✕</button></div>
<div id="soFollowPill" class="glass pill" hidden><span>👣 <b class="ugc" id="soFollowName"></b> <span>리더를 따라 걷는 중</span></span><button id="soFollowStop" type="button">멈추기</button></div>
<div id="soNote" class="glass pill" hidden><b class="ugc" id="soNoteName"></b><span id="soNoteTxt"></span></div>
<div id="soPeople" class="panel" hidden><div class="card soCard"><button class="pX" id="soPeopleX" aria-label="닫기">✕</button>
  <h1>함께 가기</h1><p class="note" id="soPeopleSub">산악회를 만들거나 초대코드로 들어가 최대 10명이 함께 걸어요. 리더를 따라 걸으면 같은 보폭으로 줄지어 걸어요.</p>
  <div id="soClub" hidden><div class="h"><b>⛰ 산악회</b><span class="cnt" id="soClubN"></span><span class="sp"></span><span class="code"><span>초대코드</span> <b id="soClubCode"></b></span><button id="soCodeCopy" type="button">초대하기</button></div>
    <div class="hint" id="soClubHint"></div><div id="soPartyL"></div>
    <div class="soPartyB"><button id="soFollow" type="button">👣 리더 따라 걷기</button><button id="soLeave" type="button">산악회 나가기</button></div></div>
  <div id="soNoClub" hidden><button id="soMake" type="button" class="soBig">⛰ 산악회 만들기</button>
    <div class="soJoin"><input id="soCodeIn" maxlength="7" placeholder="초대코드 6자리" aria-label="초대코드 6자리" autocapitalize="characters" autocomplete="off" spellcheck="false" enterkeyhint="go"><button id="soCodeGo" type="button">들어가기</button></div></div>
  <div class="h2">이 산에 있는 사람</div>
  <div id="soList"></div></div></div>
<div id="soGreet" class="panel" hidden><div class="card soCard"><button class="pX" id="soGreetX" aria-label="닫기">✕</button>
  <h1>인삿말 바꾸기</h1><p class="note">인사(1)를 할 때 머리 위에 보이는 말이에요. 한 줄에 20자까지 쓸 수 있어요.</p>
  <div id="soGreetL"></div>
  <div class="endRow"><button class="btn sec" id="soGreetR" type="button">처음 인사로</button><button class="btn" id="soGreetOk" type="button">저장</button></div></div></div>
<div id="soGuest" class="panel" hidden><div class="card soCard" id="soWall"><button class="pX" id="soGuestX" aria-label="닫기">✕</button>
  <h1>정상 방명록</h1><p class="note" id="soGuestSub">정상에 오른 사람들이 남긴 포스트잇이에요</p>
  <div id="soBoard" class="ugc"></div>
  <div id="soGuestMsg" hidden><span id="soGuestMsgT"></span><button id="soGuestG" type="button" hidden>구글로 로그인</button></div>
  <div id="soWrite" hidden>
    <div class="rw"><input id="soGuestIn" maxlength="60" placeholder="한마디 남기기 (60자)" aria-label="한마디 남기기 (60자)"></div>
    <div class="cols" id="soCols"><small>산마다 한 사람 한 장 · 다시 쓰면 바뀌어요</small></div>
    <div class="rw"><button class="btn sec" id="soGuestDel" type="button" hidden>떼기</button><button class="btn" id="soGuestOk" type="button" style="flex:1">붙이기</button></div>
  </div></div></div>
''')

SOCIAL_JS = r'''
// ---------- 함께가기·인삿말·채팅·정상 방명록 (pipeline/social_patch.py) ----------
const SO = { room: ROOM_ID, gb: '__GB__', login: { chat: __LC__, guest: __LG__ }, max: 10, fb: null, web: false, chatOk: null, clubOk: null, dmOk: null, guestOk: null };
const SO_COLS = ['#ffe680', '#ffb3c1', '#b5e3a1', '#a9d4ff', '#ffc98a'];
// 거르는 말: 띄어쓰기·숫자·기호를 빼고 비교 (보낼 때 막고, 받을 때도 가려요)
const SO_BAD = ['씨발','시발','씨바','씨빨','시빨','ㅅㅂ','ㅆㅂ','ㅄ','병신','븅신','빙신','ㅂㅅ','지랄','ㅈㄹ','좆','존나','좃','개새','개색','개세','ㄱㅅㄲ','미친놈','미친년','미친새','닥쳐','꺼져','엿먹','느금','니애미','니미럴','애미','애비','씹','섹스','야동','보지','자지','창녀','한남충','김치녀','틀딱','급식충','fuck','fuk','shit','bitch','cunt','nigg','fagg','asshole','porn','whore','slut'];
const soNorm = s => String(s).toLowerCase().replace(/[\s\d_.,·~!@#$%^&*()+=;:'"`|\\/?<>\[\]{}\-]+/g, '');
const soBad = s => { const n = soNorm(s); return SO_BAD.some(w => n.includes(w)); };
const soLink = s => /(https?:|www\.|\.(com|net|kr|io|me|ly|gg|xyz|org|co|link|site|shop)\b|t\.me|open\.kakao|discord\.|(\d[\s.\-]?){9,})/i.test(String(s));
const soCtl = c => c < 32 || c === 127 || (c >= 0x200b && c <= 0x200f) || (c >= 0x2028 && c <= 0x202e) || (c >= 0x2066 && c <= 0x2069);
const soClean = (s, n) => Array.from(String(s == null ? '' : s)).filter(ch => !soCtl(ch.codePointAt(0)) && ch !== '<' && ch !== '>').join('').replace(/\s+/g, ' ').trim().slice(0, n);
const soShow = (s, n) => { const c = soClean(s, n); return (soBad(c) || soLink(c)) ? '(가려진 말)' : c; };
const soNow = () => Date.now() + (typeof GEV_SKEW === 'number' ? GEV_SKEW : 0);
const soMe = () => { const u = SO.fb && SO.fb.auth.currentUser; return u ? u.uid : ''; };
const soAdmin = () => document.body.classList.contains('admin');
const soGoogle = () => { const u = SO.fb && SO.fb.auth.currentUser; return !!(u && !u.isAnonymous); };
let SO_BLOCK = new Set((store.get('blocked', []) || []).slice(-100));
function soBlock(uid){ if(!uid) return; SO_BLOCK.add(uid); store.set('blocked', [...SO_BLOCK].slice(-100)); toast('이 사람의 채팅과 제안을 더 보지 않아요', 3); if(SO_C.wTo && SO_C.wTo.u === uid) SO_C.wTo = null; soRenderChat(); soRenderPeople(); }
// 이름이 들어간 알림: 이름은 번역하지 않고, 뒤의 말만 번역
let soNoteT = 0;
function soNote(nick, txt, dur){ $('soNoteName').textContent = nick || ''; $('soNoteTxt').textContent = txt; $('soNote').hidden = false; soNoteT = performance.now() + (dur || 3.2)*1000; }

// ===== 인삿말 바꾸기 =====
const SO_GREET0 = GREETS.slice();
{ const g = store.get('greets', null); if(Array.isArray(g) && g.length === GREETS.length) g.forEach((t, i) => { const c = soClean(t, 20); if(c && !soBad(c) && !soLink(c)) GREETS[i] = c; }); }
function soOpenGreet(){ $('waveMenu').hidden = true; const L = $('soGreetL'); L.innerHTML = '';
  GREETS.forEach((g, i) => { const inp = document.createElement('input'); inp.maxLength = 20; inp.value = g; inp.placeholder = SO_GREET0[i]; inp.setAttribute('aria-label', '인삿말 바꾸기'); inp.oninput = () => inp.classList.remove('bad'); L.appendChild(inp); });
  $('soGreet').hidden = false; }
$('soGreetX').onclick = () => { $('soGreet').hidden = true; };
$('soGreetR').onclick = () => { [...$('soGreetL').querySelectorAll('input')].forEach((inp, i) => { inp.value = SO_GREET0[i]; inp.classList.remove('bad'); }); };
$('soGreetOk').onclick = () => { const ins = [...$('soGreetL').querySelectorAll('input')]; let bad = false;
  const vals = ins.map((inp, i) => { const c = soClean(inp.value, 20) || SO_GREET0[i]; if(soBad(c) || soLink(c)){ inp.classList.add('bad'); bad = true; } return c; });
  if(bad){ toast('고운 말로 바꿔 주세요', 2.5); return; }
  vals.forEach((v, i) => GREETS[i] = v);
  const same = vals.every((v, i) => v === SO_GREET0[i]); store.set('greets', same ? null : vals); store.set('profTs', Date.now());
  try{ cloudPush(true); }catch(e){}
  $('soGreet').hidden = true; toast('인삿말을 저장했어요', 2); pushPresence(true); };
// 다른 사람이 인사할 때: 그 사람이 고친 인삿말(gs)을 거르고 보여 줘요
function soGreetOf(pr){ if(typeof pr.gs === 'string' && pr.gs){ const s = soShow(pr.gs, 20); if(s) return s; } return SO_GREET0[Math.max(0, Math.min(SO_GREET0.length-1, num(pr.wi)|0))]; }

// ===== 산악회 (함께 가기) =====
// 같은 산(방)에서 초대코드(pt)가 같은 사람끼리 한 산악회. 리더 = 가장 먼저 들어온 사람(pj가 가장 이른 사람) → 리더가 떠나면 다음 사람이 저절로 리더.
// 따라 걷기: 리더가 지나간 길을 그대로, 산악회원은 들어온 순서대로 2.4m 간격, 리더 걸음 빠르기에 맞춰 같은 보폭으로.
const SO_P = { pt: '', pj: 0, iv: null, ia: null, ir: null, ivCode: '', ivT: 0, follow: false, goal: null, v: 0, sent: {}, hinted: new Set(), warnT: 0, buddies: 0, inv: null, invCode: '', invT: 0, chip: null, chipT: 0, chipFn: null, lead: '', joinT: 0, join: null };
const SO_GAP = 2.4;
const SO_ABC = 'abcdefghjkmnpqrstuvwxyz23456789';
const soCodeNew = () => { let s = ''; const a = new Uint32Array(6); try{ crypto.getRandomValues(a); }catch(e){ for(let i = 0; i < 6; i++) a[i] = Math.random()*1e9; } for(const x of a) s += SO_ABC[x % SO_ABC.length]; return s; };
const soCodeOk = c => typeof c === 'string' && /^[a-z0-9]{6}$/.test(c);
const soCodeIn = s => String(s || '').toLowerCase().replace(/[^a-z0-9]/g, '').slice(0, 6);
const soCodeFmt = c => String(c || '').toUpperCase();
const SO_KEY = 'neungseon.club.' + ROOM_ID;
function soPkt(pkt){ if(SO_P.pt){ pkt.pt = SO_P.pt; pkt.pj = SO_P.pj; if(SO_P.follow) pkt.pf = 1; }
  if(SO_P.iv) pkt.iv = SO_P.iv; if(SO_P.ia) pkt.ia = SO_P.ia; if(SO_P.ir) pkt.ir = SO_P.ir; pkt.gs = String(GREETS[greetIdx] || '').slice(0, 20); }
const soBuddy = a => !!(SO_P.pt && a.pt === SO_P.pt);
const soArr = v => Array.isArray(v) ? v : (v && typeof v === 'object' && 0 in v) ? [v[0], v[1], v[2]] : null;
const soFresh = v => (v = soArr(v)) && typeof v[0] === 'string' && Math.abs(soNow() - num(v[1])) < 45000;
function soPeer(id, a, pr){
  a.pid = id; a.pt = soCodeOk(pr.pt) ? pr.pt : ''; a.pj = num(pr.pj, 0) || 9e15; a.pf = pr.pf === 1;
  const me = soMe(); if(!me || SO_BLOCK.has(id)) return;
  const iv = soArr(pr.iv), ia = soArr(pr.ia), ir = soArr(pr.ir);
  if(soFresh(iv) && iv[0] === me && iv[1] !== a.lastIv){ a.lastIv = iv[1]; const code = soCodeOk(iv[2]) ? iv[2] : ''; if(code && code !== SO_P.pt) soInvite(a, code); }
  if(soFresh(ia) && ia[0] === me && ia[1] !== a.lastIa){ a.lastIa = ia[1];
    if(!SO_P.pt && SO_P.ivCode && a.pt === SO_P.ivCode) soJoin(SO_P.ivCode, SO_P.ivT || soNow(), true);
    soNote(a.nick, '님과 함께 걸어요', 3.5); SO_P.iv = null; pushPresence(true); soRenderPeople(true); }
  if(soFresh(ir) && ir[0] === me && ir[1] !== a.lastIr){ a.lastIr = ir[1]; soNote(a.nick, '님은 지금은 혼자 걷고 싶대요', 3.5); }
}
function soPartyCount(pt){ let n = 0; if(!pt) return 0; for(const a of remotes.values()) if(a.pt === pt) n++; return n; }
// 산악회원 (나 포함) — 들어온 순서대로, 맨 앞이 리더
function soMembers(){ if(!SO_P.pt) return [];
  const M = [{ uid: soMe() || 'me', pj: SO_P.pj || 9e15, me: true, pf: SO_P.follow, nick: me.nick }];
  for(const a of remotes.values()) if(soBuddy(a) && a.pid) M.push({ uid: a.pid, pj: a.pj, me: false, pf: a.pf, nick: a.nick, a });
  return M.sort((p, q) => (p.pj - q.pj) || (p.uid < q.uid ? -1 : p.uid > q.uid ? 1 : 0)); }
function soLeader(){ const M = soMembers(); return M.length ? M[0] : null; }
const soIsLeader = () => { const L = soLeader(); return !!(L && L.me); };
function soSave(){ try{ SO_P.pt ? sessionStorage.setItem(SO_KEY, JSON.stringify({ pt: SO_P.pt, pj: SO_P.pj })) : sessionStorage.removeItem(SO_KEY); }catch(e){} }
function soJoin(code, pj, quiet){ if(!soCodeOk(code)) return false;
  if(SO_P.pt && SO_P.pt !== code) soLeave(true);
  SO_P.pt = code; SO_P.pj = pj || soNow(); SO_P.joinT = performance.now(); SO_P.lead = ''; SO_P.ivCode = '';
  soSave(); pushPresence(true); soClubChat(); soRenderPeople(true); try{ soRenderChat(); }catch(e){} return true; }
function soLeave(quiet){ const was = SO_P.pt; SO_P.pt = ''; SO_P.pj = 0; SO_P.ia = null; soStopFollow(); SO_P.lead = '';
  soSave(); pushPresence(true); soClubChat(); if(!quiet && was) toast('산악회를 나왔어요', 2); soRenderPeople(true); try{ soRenderChat(); }catch(e){} }
function soMake(){ if(!soMe()){ toast('함께 가기는 neungseon.com에서 할 수 있어요', 3); return; }
  const c = soCodeNew(); soJoin(c, soNow()); soNote(soCodeFmt(c), ' 초대코드로 산악회를 만들었어요', 4); }
function soSendInvite(a){
  if(!soMe() || !a || !a.pid){ toast('함께 가기는 neungseon.com에서 할 수 있어요', 3); return; }
  if(soBuddy(a)) return;
  const last = SO_P.sent[a.pid] || 0; if(Date.now() - last < 30000){ toast('조금 뒤에 다시 제안해 주세요', 2.5); return; }
  if(SO_P.pt && soPartyCount(SO_P.pt) + 1 >= SO.max){ toast('산악회가 가득 찼어요 (최대 10명)', 2.5); return; }
  const code = SO_P.pt || SO_P.ivCode || soCodeNew(); if(!SO_P.pt){ SO_P.ivCode = code; SO_P.ivT = soNow(); }
  SO_P.sent[a.pid] = Date.now(); SO_P.iv = [a.pid, soNow(), code]; pushPresence(true);
  soNote(a.nick, '님에게 함께 가기를 제안했어요', 3); soRenderPeople(); }
function soInvite(a, code){ SO_P.inv = a; SO_P.invCode = code; SO_P.invT = performance.now() + 30000; $('soInvName').textContent = a.nick;
  $('soInvT').textContent = soPartyCount(code) > 1 ? '님이 산악회에 초대했어요' : '님이 함께 가자고 해요';
  $('soInv').hidden = false; $('soChip').hidden = true; try{ sfx.chime && sfx.chime(); }catch(e){} }
$('soInvY').onclick = () => { const a = SO_P.inv, code = SO_P.invCode; $('soInv').hidden = true; SO_P.inv = null; if(!a || !remotes.has(a.pid) || !soCodeOk(code)) return;
  if(soPartyCount(code) + 1 > SO.max){ toast('산악회가 가득 찼어요 (최대 10명)', 2.5); return; }
  soJoin(code, soNow()); SO_P.ia = [a.pid, soNow()]; pushPresence(true); soNote(a.nick, '님과 함께 걸어요', 3.5);
  setTimeout(() => { if(SO_P.pt === code && !soIsLeader() && !SO_P.follow) soAsk(null, '리더를 따라 걸을까요?', '👣 따라 걷기', () => soSetFollow(true), 10); }, 1800); };
$('soInvN2').onclick = () => { const a = SO_P.inv; $('soInv').hidden = true; SO_P.inv = null; if(a && a.pid){ SO_P.ir = [a.pid, soNow()]; pushPresence(true); } };
// 초대코드로 들어가기: 이 산에 그 코드의 산악회원이 보이면 들어가요 (몇 초 기다려요)
function soTryCode(raw){ const code = soCodeIn(raw);
  if(!soCodeOk(code)){ toast('초대코드 6자리를 넣어 주세요', 2.5); return; }
  if(!soMe()){ toast('함께 가기는 neungseon.com에서 할 수 있어요', 3); return; }
  if(code === SO_P.pt){ toast('이미 이 산악회에 있어요', 2); return; }
  SO_P.join = { code, until: performance.now() + 8000 }; $('soCodeGo').disabled = true; toast('산악회를 찾고 있어요…', 2); soJoinTick(); }
function soJoinTick(){ const J = SO_P.join; if(!J) return; const n = soPartyCount(J.code);
  if(n > 0){ SO_P.join = null; $('soCodeGo').disabled = false;
    if(n + 1 > SO.max){ toast('산악회가 가득 찼어요 (최대 10명)', 2.5); return; }
    soJoin(J.code, soNow()); $('soCodeIn').value = ''; const L = soLeader();
    if(L && !L.me){ soNote(L.nick, '님의 산악회에 들어왔어요 · 리더를 따라 걸어요', 4); soSetFollow(true); } return; }
  if(performance.now() > J.until){ SO_P.join = null; $('soCodeGo').disabled = false; toast('이 산에서 그 산악회를 찾지 못했어요 · 리더와 같은 산에 있어야 해요', 4.5); } }
// 따라 걷기
function soSlot(){ const M = soMembers(); let k = 0; for(let i = 1; i < M.length; i++){ const m = M[i]; if(m.me ? SO_P.follow : m.pf){ k++; if(m.me) return k; } } return Math.max(1, k); }
function soStopFollow(){ SO_P.follow = false; SO_P.v = 0; if(SO_P.goal && st.goal === SO_P.goal) st.goal = null; SO_P.goal = null; $('soFollowPill').hidden = true; }
function soSetFollow(on){ const L = soLeader();
  if(on && (!L || L.me)){ toast(L && L.me ? '내가 리더예요 · 산악회원들이 나를 따라 걸어요' : '따라 걸을 리더가 없어요', 2.5); on = false; }
  if(on){ SO_P.follow = true; SO_P.v = 0; st.sitting = false; st.breathing = 0; if(st.auto){ st.auto = false; refreshWalk(); }
    $('soFollowName').textContent = L.nick; $('soFollowPill').hidden = false; toast('리더를 따라 걸어요 · 직접 움직이면 멈춰요', 3); }
  else soStopFollow();
  pushPresence(true); soRenderPeople(); }
$('soFollow').onclick = () => soSetFollow(!SO_P.follow);
$('soFollowStop').onclick = e => { e.stopPropagation(); soSetFollow(false); };
$('soLeave').onclick = () => soLeave();
$('soMake').onclick = soMake;
$('soCodeGo').onclick = () => soTryCode($('soCodeIn').value);
$('soCodeIn').addEventListener('keydown', e => { if(e.key === 'Enter'){ e.preventDefault(); soTryCode($('soCodeIn').value); } });
$('soCodeIn').addEventListener('input', () => { const v = soCodeFmt(soCodeIn($('soCodeIn').value)); if($('soCodeIn').value !== v) $('soCodeIn').value = v; });
function soInviteText(){ const u = (location.origin.startsWith('http') ? location.origin + location.pathname : 'https://neungseon.com/') + '?club=' + SO_P.pt;
  return { text: (window.T || (x => x))('능선 산악회에 함께 가요! 초대코드') + ' ' + soCodeFmt(SO_P.pt), url: u }; }
$('soCodeCopy').onclick = async () => { if(!SO_P.pt) return; const t = soInviteText();
  if(document.body.classList.contains('touch') && navigator.share){ try{ await navigator.share({ title: (window.T || (x => x))('능선'), text: t.text, url: t.url }); return; }catch(e){ if(e && e.name === 'AbortError') return; } }
  try{ await navigator.clipboard.writeText(t.text + '\n' + t.url); toast('초대코드와 주소를 복사했어요', 2.5); }catch(e){ toast(soCodeFmt(SO_P.pt), 4); } };
// 리더가 지나간 길 기록 + 걸음 빠르기 (매 프레임)
function soTrack(a, dt){ if(a.px === undefined){ a.px = a.x; a.pz = a.z; a.vs = 0; a.trk = []; }
  const sp = Math.hypot(a.x - a.px, a.z - a.pz)/Math.max(dt, 1e-3); a.px = a.x; a.pz = a.z;
  a.vs += (Math.min(sp, 8) - a.vs)*Math.min(1, dt*4);
  const T = a.trk, L = T[T.length - 1]; if(!L || Math.hypot(a.x - L.x, a.z - L.z) > 0.35){ T.push({ x: a.x, z: a.z }); if(T.length > 600) T.splice(0, T.length - 500); } }
function soFollowTick(dt){
  const manual = keys.KeyW || keys.KeyA || keys.KeyS || keys.KeyD || keys.ArrowUp || keys.ArrowDown || keys.ArrowLeft || keys.ArrowRight || (joy.id !== null && Math.hypot(joy.x, joy.y) > 0.18) || st.auto || (st.goal && st.goal !== SO_P.goal) || st.sitting || st.camp;
  const Lm = soLeader(), L = Lm && !Lm.me ? Lm.a : null;
  if(manual || !L){ const why = !L && Lm && Lm.me ? '이제 내가 리더예요 · 따라 걷기를 멈췄어요' : ''; soStopFollow(); pushPresence(true); soRenderPeople(); if(why) toast(why, 3); return; }
  $('soFollowName').textContent = L.nick;
  const D = SO_GAP*soSlot(), T = L.trk || [];
  // 리더 → 지나온 길을 거꾸로 따라가며: 내 자리(D m 뒤)와 지금 내가 길 위 어디쯤인지
  let acc = 0, prev = { x: L.x, z: L.z }, P = null, bs = 0, bd = 1e9; const segs = [];
  for(let i = T.length - 1; i >= 0 && acc < D + 90; i--){ const q = T[i], sx = q.x - prev.x, sz = q.z - prev.z, sl = Math.hypot(sx, sz); if(sl < 1e-3) continue;
    let t = ((st.x - prev.x)*sx + (st.z - prev.z)*sz)/(sl*sl); t = Math.max(0, Math.min(1, t));
    const d = Math.hypot(prev.x + sx*t - st.x, prev.z + sz*t - st.z); if(d < bd){ bd = d; bs = acc + t*sl; }
    if(!P && acc + sl >= D){ const k = (D - acc)/sl; P = { x: prev.x + sx*k, z: prev.z + sz*k }; }
    segs.push([prev, q, acc, sl]); acc += sl; prev = q; }
  const dL = Math.hypot(L.x - st.x, L.z - st.z);
  if(!P){ P = dL > D ? { x: L.x + (st.x - L.x)/dL*D, z: L.z + (st.z - L.z)/dL*D } : { x: st.x, z: st.z }; }
  const onPath = bd < 4 && segs.length; const sMe = onPath ? bs : (acc < D ? dL : D + Math.hypot(P.x - st.x, P.z - st.z));
  const err = sMe - D, far = Math.hypot(P.x - st.x, P.z - st.z) > 30;
  // 자리보다 뒤면 조금 빨리, 앞이면 더 확실히 천천히 (작은 차이는 그냥 리더 빠르기 그대로 → 같은 보폭)
  const e2 = Math.abs(err) < 0.25 ? 0 : err - Math.sign(err)*0.25;
  let want = far ? 4.2 : THREE.MathUtils.clamp(L.vs + (e2 > 0 ? e2*0.6 : e2*1.8), 0, Math.max(3.4, L.vs*1.5));
  if(!far && L.vs < 0.5) want = e2 > 0 ? Math.min(want, 0.6 + e2*0.5) : 0;   // 리더가 서면 내 자리에서 멈춰요
  SO_P.v += (want - SO_P.v)*Math.min(1, dt*(want > SO_P.v ? 2.2 : 7));
  if(SO_P.v < 0.15 && want < 0.2){ if(SO_P.goal && st.goal === SO_P.goal) st.goal = null; SO_P.v = 0; return; }
  // 가는 쪽: 길 위에서 내 자리보다 1.8m 앞 (리더 쪽)
  let G = P;
  if(onPath && !far){ const s = Math.max(0, sMe - 1.8); G = { x: L.x, z: L.z }; for(const [a, b, s0, sl] of segs){ if(s <= s0 + sl){ const k = (s - s0)/sl; G = { x: a.x + (b.x - a.x)*k, z: a.z + (b.z - a.z)*k }; break; } } }
  if(Math.hypot(G.x - st.x, G.z - st.z) < 0.7){ const dx = L.x - st.x, dz = L.z - st.z, dd = Math.hypot(dx, dz) || 1; G = { x: st.x + dx/dd*1.2, z: st.z + dz/dd*1.2 }; }
  const g = SO_P.goal || (SO_P.goal = {}); g.x = G.x; g.z = G.z; g.__fs = SO_P.v; g.__ph = (L.vs > 0.3 && Math.abs(SO_P.v - L.vs) < 0.6) ? L.phase : null;
  st.goal = g; st.sitting = false; try{ goalRing.visible = false; }catch(e){} }
function soOpenPeople(hl){ SO_P.hl = hl || null; $('soPeople').hidden = false; soRenderPeople(true); }
$('soPeopleB').onclick = () => soOpenPeople(); $('soPeopleX').onclick = () => { $('soPeople').hidden = true; };
$('soPeople').addEventListener('click', e => { if(e.target === $('soPeople')) $('soPeople').hidden = true; });
// 알림 칩: 가까이 지나가는 사람에게 함께 가기 제안, 정상 방명록 안내, 따라 걷기 제안
function soAsk(nick, txt, btn, fn, dur){ $('soChipName').textContent = nick || ''; $('soChipT').textContent = txt; $('soChipB').textContent = btn; SO_P.chipFn = fn;
  $('soChip').hidden = false; SO_P.chipT = performance.now() + (dur || 9)*1000; }
$('soChipB').onclick = () => { const f = SO_P.chipFn; $('soChip').hidden = true; SO_P.chip = null; if(f) f(); };
$('soChipX').onclick = () => { $('soChip').hidden = true; SO_P.chip = null; };
function soRow(a, club){ const r = document.createElement('div'); r.className = 'soRow' + (SO_P.hl === a.pid ? ' hi' : '');
  const i = document.createElement('i'); i.style.background = hexCss(a.outfit.jacket); r.appendChild(i);
  const n = document.createElement('span'); n.className = 'nm ugc'; n.textContent = a.nick; r.appendChild(n);
  if(club && club.lead){ const t = document.createElement('span'); t.className = 'tagl'; t.textContent = '리더'; r.appendChild(t); }
  const d = document.createElement('small'); d.textContent = Math.round(Math.hypot(a.x - st.x, a.z - st.z)) + 'm'; r.appendChild(d);
  if(club){ if(a.pf){ const t = document.createElement('span'); t.className = 'tagd'; t.textContent = '따라 걷는 중'; r.appendChild(t); } }
  else if(a.pt && a.pt !== SO_P.pt && soPartyCount(a.pt) > 1){ const t = document.createElement('span'); t.className = 'tagd mute'; t.textContent = '다른 산악회'; r.appendChild(t); }
  else if(Date.now() - (SO_P.sent[a.pid] || 0) < 30000){ const t = document.createElement('span'); t.className = 'tagd'; t.textContent = '제안했어요'; r.appendChild(t); }
  else { const b = document.createElement('button'); b.className = 'go'; b.textContent = '함께 가기'; b.onclick = () => soSendInvite(a); r.appendChild(b); }
  const k = document.createElement('button'); k.textContent = '⋯'; k.setAttribute('aria-label', '더 보기');
  k.onclick = e => soMenuAt(e, [['💬 귓속말 보내기', () => soWhisperTo(a.pid, a.nick)], ['이 사람 가리기', () => soBlock(a.pid)]]); r.appendChild(k);
  return r; }
function soMeRow(lead){ const r = document.createElement('div'); r.className = 'soRow me';
  const i = document.createElement('i'); i.style.background = hexCss(me.outfit.jacket); r.appendChild(i);
  const n = document.createElement('span'); n.className = 'nm'; const nn = document.createElement('span'); nn.className = 'ugc'; nn.textContent = me.nick; n.appendChild(nn);
  const y = document.createElement('small'); y.textContent = ' (나)'; n.appendChild(y); r.appendChild(n);
  if(lead){ const t = document.createElement('span'); t.className = 'tagl'; t.textContent = '리더'; r.appendChild(t); }
  if(SO_P.follow){ const t = document.createElement('span'); t.className = 'tagd'; t.textContent = '따라 걷는 중'; r.appendChild(t); }
  return r; }
let soPeopleSig = '';
function soRenderPeople(force){ if($('soPeople').hidden){ soPeopleSig = ''; return; }
  const list = [...remotes.values()].filter(a => a.pid && !SO_BLOCK.has(a.pid)).sort((p, q) => Math.hypot(p.x - st.x, p.z - st.z) - Math.hypot(q.x - st.x, q.z - st.z));
  const M = soMembers();
  const sig = [SO.web, SO_P.follow, SO_P.pt, SO_P.hl, M.map(m => m.uid + (m.pf ? 'f' : '')).join(','), ...list.map(a => [a.pid, a.nick, a.pt, a.pf, Math.round(Math.hypot(a.x - st.x, a.z - st.z)/5), Date.now() - (SO_P.sent[a.pid] || 0) < 30000].join(','))].join('|');
  if(sig === soPeopleSig && force !== true) return; soPeopleSig = sig;
  const L = $('soList'); L.innerHTML = '';
  const others = list.filter(a => !soBuddy(a));
  if(!SO.web){ L.innerHTML = '<div class="empty">함께 가기는 neungseon.com에서 할 수 있어요</div>'; }
  else if(!others.length){ L.innerHTML = '<div class="empty">지금은 이 산에 다른 사람이 없어요</div>'; }
  others.forEach(a => L.appendChild(soRow(a)));
  const inClub = !!SO_P.pt; $('soClub').hidden = !inClub; $('soNoClub').hidden = inClub || !SO.web;
  if(inClub){ $('soClubCode').textContent = soCodeFmt(SO_P.pt); $('soClubN').textContent = M.length + '/' + SO.max;
    const PL = $('soPartyL'); PL.innerHTML = ''; M.forEach((m, i) => PL.appendChild(m.me ? soMeRow(i === 0) : soRow(m.a, { lead: i === 0 })));
    const lead = M.length && M[0].me; $('soFollow').hidden = lead;
    $('soFollow').textContent = SO_P.follow ? '따라 걷기 멈추기' : '👣 리더 따라 걷기'; $('soFollow').classList.toggle('on', SO_P.follow);
    $('soClubHint').textContent = lead ? (M.length > 1 ? '내가 리더예요 · 산악회원들이 줄지어 따라와요' : '초대코드를 알려 주면 최대 10명까지 함께 걸을 수 있어요') : '리더를 따라 걸으면 같은 보폭으로 줄지어 걸어요'; } }
// 매 프레임 (updateRemotes 앞에서)
let soAcc = 0, soStarted = false;
function soTick(dt){
  if(st.started && !soStarted){ soStarted = true; document.body.classList.add('soOn');
    try{ const q = new URLSearchParams(location.search).get('club'); if(q && soCodeOk(soCodeIn(q))) setTimeout(() => soTryCode(q), 2500); }catch(e){} }
  const nowMs = performance.now();
  if(soNoteT && nowMs > soNoteT){ soNoteT = 0; $('soNote').hidden = true; }
  if(SO_P.invT && nowMs > SO_P.invT){ SO_P.invT = 0; $('soInv').hidden = true; SO_P.inv = null; }
  if(SO_P.chipT && (nowMs > SO_P.chipT || (SO_P.chip && (soBuddy(SO_P.chip) || !remotes.has(SO_P.chip.pid))))){ SO_P.chipT = 0; $('soChip').hidden = true; SO_P.chip = null; }
  if(SO_P.pt) for(const a of remotes.values()) if(soBuddy(a)) soTrack(a, dt);
  // 리더 따라 걷기: 직접 움직이면(키·조이스틱·땅 누르기) 멈춤
  if(SO_P.follow) soFollowTick(dt);
  if(nowMs - soAcc < 500) return; const step = Math.min(5, (nowMs - soAcc)/1000); soAcc = nowMs;
  soJoinTick();
  // 오래된 신호 정리
  for(const k of ['iv', 'ia', 'ir']) if(SO_P[k] && Math.abs(soNow() - num(SO_P[k][1])) > 40000){ SO_P[k] = null; if(k === 'iv') SO_P.ivCode = ''; pushPresence(true); }
  // 리더가 바뀌면 알려요 (리더가 산을 떠나면 다음으로 먼저 들어온 사람이 저절로 리더)
  if(SO_P.pt){ const Lm = soLeader(), id = Lm ? Lm.uid : '';
    if(SO_P.lead && id !== SO_P.lead && nowMs - SO_P.joinT > 5000){ if(Lm.me) toast('리더가 산을 떠나 이제 내가 산악회 리더예요', 4); else soNote(Lm.nick, '님이 새 리더가 됐어요', 3.5); }
    SO_P.lead = id; }
  // 이름표: 누르면 함께 가기 창, 산악회원은 🤝, 리더는 👑
  let buddies = 0, near = 1e9; const lead = SO_P.pt ? soLeader() : null;
  for(const [k, a] of remotes){ const b = soBuddy(a); if(b){ buddies++; near = Math.min(near, Math.hypot(a.x - st.x, a.z - st.z)); }
    const el = tagEls.get('p' + k); if(el){ if(!el._so){ el._so = true; el.classList.add('peer'); el.querySelector('.n').addEventListener('click', () => soOpenPeople(k)); } el.classList.toggle('buddy', b); el.classList.toggle('lead', !!(b && lead && lead.uid === a.pid)); }
    // 가까이 처음 지나가면 '함께 가기 제안' 알림 한 번
    if(SO.web && st.started && !b && a.pid && !SO_P.hinted.has(a.pid) && !SO_BLOCK.has(a.pid) && Math.hypot(a.x - st.x, a.z - st.z) < 12 && $('soInv').hidden && $('soChip').hidden){
      SO_P.hinted.add(a.pid); SO_P.chip = a; soAsk(a.nick, '님이 가까이 있어요', '함께 가기 제안', () => soSendInvite(a), 9); SO_P.chip = a; } }
  if(SO_P.pt){
    if(buddies && near > 70 && !SO_P.follow && performance.now() - SO_P.warnT > 60000){ SO_P.warnT = performance.now(); toast('산악회원과 멀어졌어요 · 잠시 기다려 볼까요?', 3.5); }
    if(SO_P.buddies && !buddies){ toast('함께하던 산악회원이 모두 산을 떠났어요', 3); if(SO_P.follow) soSetFollow(false); } }
  SO_P.buddies = buddies;
  $('soPeopleB').classList.toggle('on', !!SO_P.pt); const pb = $('soPBadge'); pb.hidden = !SO_P.pt; if(SO_P.pt) pb.textContent = String(buddies + 1);
  soRenderPeople();
}
// 다시 불러와도 같은 산악회 (이 탭에서만)
try{ const c = JSON.parse(sessionStorage.getItem(SO_KEY) || 'null'); if(c && soCodeOk(c.pt)){ SO_P.pt = c.pt; SO_P.pj = num(c.pj) || 0; } }catch(e){}
// 지도에 산악회원 표시 (초록 고리, 리더는 금빛)
function soMapRing(mctx, toU, toV, big){ if(!SO_P.pt) return; const L = soLeader();
  for(const a of remotes.values()){ if(!soBuddy(a)) continue; const ld = L && L.uid === a.pid; mctx.strokeStyle = ld ? '#ffd86b' : '#7dff9a'; mctx.lineWidth = big ? 2.5 : 5; mctx.beginPath(); mctx.arc(toU(a.x), toV(a.z), big ? 9 : 18, 0, 7); mctx.stroke(); } }

// ===== 작은 메뉴 (신고·가리기·지우기) =====
function soMenuAt(e, items){ e.stopPropagation(); const m = $('soMenu'); m.innerHTML = '';
  items.forEach(([t, f]) => { const b = document.createElement('button'); b.textContent = t; b.onclick = ev => { ev.stopPropagation(); m.hidden = true; f(); }; m.appendChild(b); });
  m.hidden = false; const w = m.offsetWidth, h = m.offsetHeight; m.style.left = Math.max(8, Math.min(innerWidth - w - 8, e.clientX)) + 'px'; m.style.top = Math.max(8, Math.min(innerHeight - h - 8, e.clientY)) + 'px'; }
addEventListener('pointerdown', e => { const m = $('soMenu'); if(!m.hidden && !m.contains(e.target)) m.hidden = true; }, true);
function soFlag(kind, room, id){ const fb = SO.fb, me = soMe(); if(!fb || !me) return;
  fb.D.set(fb.D.ref(fb.db, `flags/${kind}/${room}/${id}/${me}`), true).then(() => toast('신고했어요 · 여러 사람이 신고하면 가려져요', 3)).catch(() => toast('보내지 못했어요 · 잠시 후 다시 해 주세요', 2.5)); }
function soFlagListen(kind, room, cb){ const fb = SO.fb; fb.D.onValue(fb.D.ref(fb.db, `flags/${kind}/${room}`), s => { const v = s.val() || {}, out = {}; for(const k in v) out[k] = Object.keys(v[k] || {}).length; cb(out); }, () => {}); }

// ===== 채팅: 전체 · 산악회 · 귓속말 + 이모티콘 + 켜고 끄기 =====
// 전체: chat/<산>   산악회: pchat/<초대코드>   귓속말: dm/<받는 사람>/<id> (보낸 사람 것도 dm/<나>/<id>에 같이) — 귓속말은 받는 사람과 보낸 사람만 읽어요
const SO_EMO = ['😊','😄','🥰','😂','🤗','👍','👏','🙌','🙏','💪','👋','🔥','✨','🎉','❤️','🧡','💚','😮','😢','😴','⛰️','🏔️','🌄','🌅','🌙','⭐','🍁','🌸','☕','🍙','🥾','📸'];
const soEmoOnly = s => { const t = String(s).replace(/\s+/g, ''); try{ return t.length > 0 && t.length <= 12 && /^(\p{Extended_Pictographic}|️)+$/u.test(t); }catch(e){ return false; } };
const SO_C = { tab: 'all', box: { all: new Map(), club: new Map(), dm: new Map() }, flags: {}, pflags: {}, unread: { all: 0, club: 0, dm: 0 }, last: 0, cleaned: 0,
  off: !!store.get('chatOff', 0), wTo: null, clubOff: null, clubFlagOff: null, clubCode: '', dmOff: null, dmUid: '' };
function soChatOn(){ return !SO_C.off; }
function soSetChatOff(off){ SO_C.off = !!off; store.set('chatOff', off ? 1 : 0); document.body.classList.toggle('chatOff', SO_C.off);
  if(off){ for(const a of remotes.values()) if(a.sayChat){ a.sayT = 0; a.sayChat = false; } SO_C.unread = { all: 0, club: 0, dm: 0 }; }
  soBadges(); soRenderChat(); toast(off ? '채팅을 껐어요 · 말풍선과 알림이 보이지 않아요' : '채팅을 켰어요', 2.5); }
document.body.classList.toggle('chatOff', SO_C.off);
function soBadges(){ const U = SO_C.unread, n = SO_C.off ? 0 : U.all + U.club + U.dm, b = $('soBadge'); b.hidden = !n; if(n) b.textContent = n > 9 ? '9+' : n;
  for(const t of ['all', 'club', 'dm']){ const e = $('soTabN_' + t); if(e){ e.hidden = !U[t] || SO_C.off; e.textContent = U[t] > 9 ? '9+' : U[t]; } } }
function soOpenChat(on){ const c = $('soChat'); c.hidden = on === undefined ? !c.hidden : !on; $('soChatB').classList.toggle('on', !c.hidden);
  if(!c.hidden){ SO_C.unread[SO_C.tab] = 0; soBadges(); soRenderChat(); if(!document.body.classList.contains('touch') && !SO_C.off) setTimeout(() => $('soChatIn').focus(), 30); }
  else { $('soChatIn').blur(); $('soEmo').hidden = true; } }
function soTab(t){ SO_C.tab = t; SO_C.unread[t] = 0; soBadges(); $('soEmo').hidden = true; soRenderChat(); }
for(const t of ['all', 'club', 'dm']) $('soTab_' + t).onclick = () => soTab(t);
$('soChatB').onclick = () => soOpenChat(); $('soChatX').onclick = () => soOpenChat(false);
$('soChatOff').onclick = () => soSetChatOff(!SO_C.off); $('soChatOn').onclick = () => soSetChatOff(false);
$('soChatG').onclick = () => { try{ googleLogin().then(() => soRenderChat()); }catch(e){} };
$('soEmoB').onclick = e => { e.preventDefault(); $('soEmo').hidden = !$('soEmo').hidden; };
SO_EMO.forEach(em => { const b = document.createElement('button'); b.type = 'button'; b.textContent = em; b.onclick = () => { const inp = $('soChatIn'), s = inp.selectionStart ?? inp.value.length, e2 = inp.selectionEnd ?? s;
  const v = inp.value.slice(0, s) + em + inp.value.slice(e2); if(Array.from(v).length > 80) return; inp.value = v; const p = s + em.length; try{ inp.setSelectionRange(p, p); }catch(_){}
  if(!document.body.classList.contains('touch')) inp.focus(); }; $('soEmo').appendChild(b); });
$('soWhoX').onclick = () => { SO_C.wTo = null; soRenderChat(); };
function soWhisperTo(uid, nick){ if(!uid || uid === soMe()) return; SO_C.wTo = { u: uid, n: safeNick(nick) }; $('soPeople').hidden = true; soOpenChat(true); soTab('dm');
  if(!document.body.classList.contains('touch')) setTimeout(() => $('soChatIn').focus(), 30); }
addEventListener('keydown', e => { if(!st.started) return;
  if(e.target && e.target.id === 'soChatIn'){ if(e.key === 'Escape'){ e.preventDefault(); soOpenChat(false); try{ canvas.focus(); }catch(_){} } return; }
  if(e.key === 'Enter' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'BUTTON' && document.querySelectorAll('.panel:not([hidden])').length === 0){ e.preventDefault(); soOpenChat(true); if(!SO_C.off) $('soChatIn').focus(); } });
function soMsgEl(id, m, kind){ const meId = soMe(), mine = m.u === meId, d = document.createElement('div'); d.className = 'm' + (mine ? ' me' : '') + (soEmoOnly(m.x) ? ' emo' : '');
  const b = document.createElement('b');
  if(kind === 'dm'){ const other = mine ? safeNick(m.tn || '') : safeNick(m.n); b.textContent = mine ? '→ ' + other : other; }
  else b.textContent = safeNick(m.n);
  d.appendChild(b); d.appendChild(document.createTextNode(soShow(m.x, 80)));
  const t = new Date(num(m.t)); const sm = document.createElement('small'); sm.textContent = t.getHours() + ':' + String(t.getMinutes()).padStart(2, '0'); d.appendChild(sm);
  d.onclick = e => { const it = [], other = kind === 'dm' && mine ? m.to : m.u, on = kind === 'dm' && mine ? (m.tn || '') : m.n;
    if(other && other !== meId){ it.push(['💬 귓속말 보내기', () => soWhisperTo(other, on)]);
      if(kind !== 'dm') it.push(['신고하기', () => soFlag('chat', kind === 'club' ? 'p-' + SO_P.pt : SO.room, id)]);
      it.push(['이 사람 가리기', () => soBlock(other)]); }
    const path = kind === 'all' ? `chat/${SO.room}/${id}` : kind === 'club' ? `pchat/${SO_P.pt}/${id}` : `dm/${meId}/${id}`;
    if(kind === 'dm') it.push(['지우기', () => SO.fb.D.remove(SO.fb.D.ref(SO.fb.db, path)).then(() => toast('지웠어요', 1.5)).catch(() => {})]);
    else if(soAdmin() || mine) it.push([soAdmin() && !mine ? '지우기 (관리자)' : '지우기', () => SO.fb.D.remove(SO.fb.D.ref(SO.fb.db, path)).then(() => toast('지웠어요', 1.5)).catch(() => {})]);
    if(it.length) soMenuAt(e, it); };
  return d; }
function soRenderChat(){ const box = $('soMsgs'); if($('soChat').hidden) return;
  const tab = SO_C.tab; for(const t of ['all', 'club', 'dm']) $('soTab_' + t).classList.toggle('on', t === tab);
  $('soChatOff').textContent = SO_C.off ? '켜기' : '끄기'; $('soChatOff').classList.toggle('off', SO_C.off);
  const need = SO.login.chat && !soGoogle(), ready = SO.web && (tab === 'all' ? SO.chatOk !== false : tab === 'club' ? SO.clubOk !== false : SO.dmOk !== false);
  const noClub = tab === 'club' && !SO_P.pt, noWho = tab === 'dm' && !SO_C.wTo;
  $('soChatOffBox').hidden = !SO_C.off; $('soChatBody').hidden = SO_C.off;
  $('soChatLogin').hidden = SO_C.off || !SO.web || !need || !ready; $('soChatF').hidden = SO_C.off || !SO.web || need || !ready || noClub || noWho;
  $('soWho').hidden = SO_C.off || tab !== 'dm' || !SO_C.wTo; if(SO_C.wTo) $('soWhoN').textContent = SO_C.wTo.n;
  $('soChatIn').placeholder = tab === 'club' ? '산악회원에게만 보여요' : tab === 'dm' ? '귓속말은 이 사람에게만 보여요' : '고운 말로 인사해 보세요';
  if(SO_C.off) return;
  const atEnd = box.scrollTop + box.clientHeight > box.scrollHeight - 30; box.innerHTML = '';
  const empty = t => { const d = document.createElement('div'); d.className = 'empty'; d.textContent = t; box.appendChild(d); };
  if(!SO.web){ empty('채팅과 방명록은 neungseon.com에서 열려요'); return; }
  if(!ready){ empty('채팅을 준비하고 있어요. 곧 열려요.'); return; }
  if(noClub){ empty('산악회에 들어가면 산악회원끼리 이야기할 수 있어요'); const b = document.createElement('button'); b.className = 'soLink'; b.textContent = '⛰ 산악회 만들기·들어가기'; b.onclick = () => { soOpenChat(false); soOpenPeople(); }; box.appendChild(b); return; }
  const cut = soNow() - 86400000, F = tab === 'club' ? SO_C.pflags : tab === 'all' ? SO_C.flags : {}; let n = 0;
  for(const [id, m] of [...SO_C.box[tab]].sort((p, q) => num(p[1].t) - num(q[1].t))){
    if(num(m.t) < cut || SO_BLOCK.has(m.u) || (F[id] || 0) >= 3) continue;
    if(tab === 'dm' && SO_C.wTo && m.u !== SO_C.wTo.u && m.to !== SO_C.wTo.u) continue;
    n++; box.appendChild(soMsgEl(id, m, tab)); }
  if(tab === 'dm' && !SO_C.wTo){ // 받는 사람 고르기: 이 산에 있는 사람 + 귓속말 나눈 사람
    const seen = new Map(); for(const m of SO_C.box.dm.values()){ const mine = m.u === soMe(), o = mine ? m.to : m.u; if(o && !SO_BLOCK.has(o)) seen.set(o, mine ? (m.tn || '') : m.n); }
    for(const a of remotes.values()) if(a.pid && !SO_BLOCK.has(a.pid)) seen.set(a.pid, a.nick);
    box.innerHTML = ''; empty(seen.size ? '누구에게 귓속말을 보낼까요?' : '지금은 귓속말을 보낼 사람이 없어요');
    const W = document.createElement('div'); W.className = 'soWhoL'; for(const [u, nn] of seen){ const b = document.createElement('button'); b.className = 'ugc'; b.textContent = safeNick(nn);
      const un = [...SO_C.box.dm.values()].some(m => m.u === u && num(m.t) > (SO_C.dmSeen || 0)); if(un) b.classList.add('new'); b.onclick = () => soWhisperTo(u, nn); W.appendChild(b); }
    box.appendChild(W); return; }
  if(!n) empty(tab === 'dm' ? '귓속말은 받는 사람과 나만 볼 수 있어요' : tab === 'club' ? '산악회원끼리만 보이는 이야기예요' : '아직 대화가 없어요. 먼저 인사를 건네 보세요.');
  if(tab === 'dm') SO_C.dmSeen = soNow();
  if(atEnd || n < 8) box.scrollTop = box.scrollHeight; }
$('soChatF').addEventListener('submit', async e => { e.preventDefault(); const inp = $('soChatIn'), fb = SO.fb, meId = soMe(); const x = soClean(inp.value, 80); if(!x || !fb || !meId || SO_C.off) return;
  if(soBad(x) || soLink(x)){ toast('고운 말로 적어 주세요 · 주소(링크)와 전화번호는 쓸 수 없어요', 3.5); return; }
  if(Date.now() - SO_C.last < 3000){ toast('조금 천천히 보내 주세요', 2); return; }
  if(SO.login.chat && !soGoogle()){ soRenderChat(); return; }
  const tab = SO_C.tab, D = fb.D, nick = safeNick(meNick()), up = { [`chatlast/${meId}`]: D.serverTimestamp() };
  if(tab === 'all'){ const key = D.push(D.ref(fb.db, `chat/${SO.room}`)).key; up[`chat/${SO.room}/${key}`] = { u: meId, n: nick, x, t: D.serverTimestamp() }; }
  else if(tab === 'club'){ if(!SO_P.pt) return; const key = D.push(D.ref(fb.db, `pchat/${SO_P.pt}`)).key; up[`pchat/${SO_P.pt}/${key}`] = { u: meId, n: nick, x, t: D.serverTimestamp() }; }
  else { const W = SO_C.wTo; if(!W) return; const key = D.push(D.ref(fb.db, `dm/${W.u}`)).key, msg = { u: meId, n: nick, x, to: W.u, tn: W.n, t: D.serverTimestamp() };
    up[`dm/${W.u}/${key}`] = msg; up[`dm/${meId}/${key}`] = msg; }
  SO_C.last = Date.now();
  try{ await D.update(D.ref(fb.db), up); inp.value = ''; $('soEmo').hidden = true; if(tab !== 'dm'){ say(x); st.sayT = 5; } }
  catch(err){ console.warn(err); SO_C.last = 0; toast(tab === 'all' ? '보내지 못했어요 · 잠시 후 다시 해 주세요' : '아직 준비 중이에요 · 곧 열려요', 2.5); } });
function meNick(){ return me.nick; }
// 받은 말: 말풍선·알림 (채팅을 끄면 둘 다 안 보여요)
function soGot(kind, id, v){ const meId = soMe(); if(v.u === meId || SO_BLOCK.has(v.u) || soNow() - num(v.t) > 20000 || SO_C.off) return;
  const txt = soShow(v.x, 80);
  if(kind !== 'dm') for(const a of remotes.values()) if(a.pid === v.u){ a.say = txt; a.sayT = 5; a.sayChat = true; }
  if(kind === 'dm') soNote(safeNick(v.n), '님의 귓속말이 왔어요 💬', 3.5);
  if($('soChat').hidden || SO_C.tab !== kind){ SO_C.unread[kind]++; soBadges(); } }
function soListen(fb, path, kind, okKey){ const D = fb.D, q = D.query(D.ref(fb.db, path), D.limitToLast(50)), M = SO_C.box[kind];
  const u1 = D.onChildAdded(q, s => { const v = s.val(); if(!v || typeof v !== 'object') return; SO[okKey] = true;
      if(num(v.t) < soNow() - 86400000){ if(SO_C.cleaned < 8){ SO_C.cleaned++; D.remove(D.ref(fb.db, `${path}/${s.key}`)).catch(() => {}); } return; }
      M.set(s.key, v); soGot(kind, s.key, v); soRenderChat(); },
    err => { SO[okKey] = false; console.warn('채팅 연결 실패', path, err); soRenderChat(); });
  const u2 = D.onChildRemoved(q, s => { M.delete(s.key); soRenderChat(); });
  return () => { try{ u1(); u2(); }catch(e){} }; }
function soChatStart(fb){ soListen(fb, `chat/${SO.room}`, 'all', 'chatOk'); soFlagListen('chat', SO.room, f => { SO_C.flags = f; soRenderChat(); }); soClubChat(); soDmChat(); }
// 산악회가 바뀌면 산악회 채팅도 바꿔 들어요
function soClubChat(){ const fb = SO.fb; if(!fb || SO_C.clubCode === SO_P.pt) return;
  if(SO_C.clubOff){ SO_C.clubOff(); SO_C.clubOff = null; } SO_C.box.club.clear(); SO_C.unread.club = 0; SO_C.pflags = {}; SO.clubOk = null; SO_C.clubCode = SO_P.pt;
  if(SO_P.pt){ SO_C.clubOff = soListen(fb, `pchat/${SO_P.pt}`, 'club', 'clubOk'); soFlagListen('chat', 'p-' + SO_P.pt, f => { if(SO_C.clubCode === SO_P.pt){ SO_C.pflags = f; soRenderChat(); } }); }
  soBadges(); }
// 귓속말 받는 칸: 로그인으로 내 아이디가 바뀌면 다시
function soDmChat(){ const fb = SO.fb, meId = soMe(); if(!fb || !meId || SO_C.dmUid === meId) return;
  if(SO_C.dmOff){ SO_C.dmOff(); SO_C.dmOff = null; } SO_C.box.dm.clear(); SO_C.dmUid = meId; SO.dmOk = null;
  SO_C.dmOff = soListen(fb, `dm/${meId}`, 'dm', 'dmOk'); }
setInterval(() => { if(SO.fb) soDmChat(); }, 3000);

// ===== 정상 방명록 =====
const SO_G = { notes: {}, flags: {}, col: 0, started: false, prompted: false, board: null };
function soReached(){ return !!(st.inSummit || st.finished || st.camp); }
function soOpenGuest(){ soGuestStart(); $('soGuest').hidden = false; soRenderGuest(); }
$('soGuestX').onclick = () => { $('soGuest').hidden = true; };
$('soGuest').addEventListener('click', e => { if(e.target === $('soGuest')) $('soGuest').hidden = true; });
$('soGuestG').onclick = () => { try{ googleLogin().then(() => soRenderGuest()); }catch(e){} };
SO_COLS.forEach((c, i) => { const b = document.createElement('button'); b.type = 'button'; b.style.background = c; b.setAttribute('aria-label', 'color ' + (i+1)); b.onclick = () => { SO_G.col = i; soRenderCols(); }; $('soCols').insertBefore(b, $('soCols').lastElementChild); });
function soRenderCols(){ [...$('soCols').querySelectorAll('button')].forEach((b, i) => b.classList.toggle('on', i === SO_G.col)); }
function soNoteList(){ const me = soMe(); return Object.entries(SO_G.notes).filter(([u, v]) => v && typeof v === 'object' && !SO_BLOCK.has(u) && ((SO_G.flags[u] || 0) < 3 || u === me)).sort((p, q) => num(q[1].t) - num(p[1].t)).slice(0, 80); }
function soRenderGuest(){ if($('soGuest').hidden) return; const B = $('soBoard'), me = soMe(), mine = SO_G.notes[me];
  B.innerHTML = ''; const list = soNoteList();
  if(!SO.web || SO.guestOk === false){ B.innerHTML = '<div class="empty"></div>'; B.firstChild.textContent = SO.web ? '방명록을 준비하고 있어요. 곧 열려요.' : '채팅과 방명록은 neungseon.com에서 열려요'; }
  else if(!list.length){ B.innerHTML = '<div class="empty">아직 붙은 포스트잇이 없어요. 첫 장을 붙여 보세요.</div>'; }
  for(const [u, v] of list){ const d = document.createElement('div'); d.className = 'pi' + (u === me ? ' mine' : ''); d.style.background = SO_COLS[num(v.c) | 0] || SO_COLS[0];
    d.style.transform = `rotate(${((u.charCodeAt(0) + u.charCodeAt(u.length-1)) % 7 - 3) * 0.7}deg)`;
    const w = document.createElement('div'); w.className = 'w'; w.textContent = soShow(v.x, 60); d.appendChild(w);
    const by = document.createElement('div'); by.className = 'by'; const nn = document.createElement('span'); nn.textContent = safeNick(v.n); const dt = document.createElement('span'); const t = new Date(num(v.t)); dt.textContent = `${t.getFullYear()}.${t.getMonth()+1}.${t.getDate()}`; by.appendChild(nn); by.appendChild(dt); d.appendChild(by);
    d.onclick = e => { const it = []; if(u !== me){ it.push(['신고하기', () => soFlag('guest', SO.gb, u)]); it.push(['이 사람 가리기', () => soBlock(u)]); }
      if(soAdmin() && u !== me) it.push(['지우기 (관리자)', () => SO.fb.D.remove(SO.fb.D.ref(SO.fb.db, `guest/${SO.gb}/${u}`)).then(() => toast('지웠어요', 1.5)).catch(() => {})]);
      if(it.length) soMenuAt(e, it); };
    B.appendChild(d); }
  // 쓰기
  const msg = $('soGuestMsg'), gBtn = $('soGuestG'), W = $('soWrite'); let why = '';
  if(!SO.web || SO.guestOk === false) why = '-';
  else if(!soReached()) why = '정상에 오르면 포스트잇을 붙일 수 있어요';
  else if(SO.login.guest && !soGoogle()) why = '구글로 로그인해야 쓸 수 있어요';
  W.hidden = !!why; msg.hidden = !why || why === '-'; $('soGuestMsgT').textContent = why === '-' ? '' : why; gBtn.hidden = why !== '구글로 로그인해야 쓸 수 있어요';
  if(!why){ $('soGuestDel').hidden = !mine; $('soGuestOk').textContent = mine ? '고쳐 붙이기' : '붙이기';
    if(mine && !W._filled){ W._filled = true; $('soGuestIn').value = soClean(mine.x, 60); SO_G.col = num(mine.c) | 0; } soRenderCols(); }
}
$('soGuestOk').onclick = async () => { const fb = SO.fb, me = soMe(), x = soClean($('soGuestIn').value, 60); if(!fb || !me || !x) return;
  if(soBad(x) || soLink(x)){ toast('고운 말로 적어 주세요 · 주소(링크)와 전화번호는 쓸 수 없어요', 3.5); return; }
  try{ await fb.D.set(fb.D.ref(fb.db, `guest/${SO.gb}/${me}`), { n: safeNick(meNick()), x, c: SO_G.col, t: fb.D.serverTimestamp() }); toast('포스트잇을 붙였어요', 2.5); }
  catch(e){ console.warn(e); toast('조금 천천히 보내 주세요', 2.5); } };
$('soGuestDel').onclick = async () => { const fb = SO.fb, me = soMe(); if(!fb || !me) return;
  try{ await fb.D.remove(fb.D.ref(fb.db, `guest/${SO.gb}/${me}`)); $('soGuestIn').value = ''; $('soWrite')._filled = false; toast('포스트잇을 뗐어요', 2); }catch(e){ toast('보내지 못했어요 · 잠시 후 다시 해 주세요', 2.5); } };
function soGuestStart(){ if(SO_G.started || !SO.fb) return; SO_G.started = true; const fb = SO.fb, D = fb.D;
  D.onValue(D.query(D.ref(fb.db, `guest/${SO.gb}`), D.orderByChild('t'), D.limitToLast(120)), s => { SO_G.notes = s.val() || {}; SO.guestOk = true; soRenderGuest(); soBoardDraw(); }, err => { SO.guestOk = false; console.warn('방명록 연결 실패', err); soRenderGuest(); });
  soFlagListen('guest', SO.gb, f => { SO_G.flags = f; soRenderGuest(); soBoardDraw(); }); }
// 정상 옆 게시판 (3D): 최근 포스트잇 12장
function soBoardMake(){ if(SO_G.board || typeof CAMP === 'undefined') return;
  const top = trail[trail.length-1]; let best = null, bs = 1e9;
  for(let r = 3.2; r <= 7; r += 0.6) for(let a = 0; a < 6.28; a += 0.26){ const x = CAMP.x + Math.cos(a)*r, z = CAMP.z + Math.sin(a)*r, h = heightAt(x, z);
    let sl = 0; for(let q = 0; q < 8; q++){ const aa = q*0.785; sl = Math.max(sl, Math.abs(heightAt(x + Math.cos(aa)*1.2, z + Math.sin(aa)*1.2) - h)); }
    let clr = 0; for(const s of (CAMP.seats || [])) clr = Math.max(clr, 2.2 - Math.hypot(s.x - x, s.z - z));
    if(typeof FLAG !== 'undefined' && FLAG && Math.hypot(FLAG.x - x, FLAG.z - z) < 3) continue;
    if(Math.hypot(top.x - x, top.z - z) < 2) continue;
    const sc = sl*3 + clr*2 + Math.abs(r - 4.5)*0.15; if(sc < bs){ bs = sc; best = { x, z }; } }
  if(!best) return; const y = heightAt(best.x, best.z);
  const g = new THREE.Group(); g.position.set(best.x, y, best.z); g.rotation.y = Math.atan2(CAMP.x - best.x, CAMP.z - best.z);
  const wood = new THREE.MeshStandardMaterial({ color: 0x6b4a2e, roughness: 0.9 });
  for(const sx of [-0.62, 0.62]){ const p = new THREE.Mesh(new THREE.BoxGeometry(0.09, 1.7, 0.09), wood); p.position.set(sx, 0.85, 0); p.castShadow = true; g.add(p); }
  const roof = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.06, 0.3), wood); roof.position.set(0, 1.74, 0.02); roof.rotation.x = -0.12; g.add(roof);
  const cv = document.createElement('canvas'); cv.width = 512; cv.height = 340; const tex = new THREE.CanvasTexture(cv); tex.colorSpace = THREE.SRGBColorSpace; tex.anisotropy = 4;
  const face = new THREE.Mesh(new THREE.PlaneGeometry(1.24, 0.82), new THREE.MeshStandardMaterial({ map: tex, roughness: 0.95 }));
  face.position.set(0, 1.18, 0.05); g.add(face);
  const back = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.88, 0.05), wood); back.position.set(0, 1.18, 0.0); g.add(back);
  scene.add(g); SO_G.board = { g, cv, tex, x: best.x, z: best.z }; soBoardDraw(); }
function soBoardDraw(){ const B = SO_G.board; if(!B) return; const c = B.cv.getContext('2d');
  c.fillStyle = '#b88b5a'; c.fillRect(0, 0, 512, 340); for(let i = 0; i < 900; i++){ c.fillStyle = `rgba(${60+Math.random()*40|0},${40+Math.random()*30|0},20,${Math.random()*0.18})`; c.fillRect(Math.random()*512, Math.random()*340, 2, 2); }
  c.fillStyle = '#fff7e6'; c.font = 'bold 26px sans-serif'; c.textAlign = 'center'; c.fillText('📝', 256, 30);
  const list = soNoteList().slice(0, 12);
  list.forEach(([u, v], i) => { const col = i % 4, row = (i / 4) | 0, x = 14 + col*124, y = 42 + row*98;
    c.save(); c.translate(x + 56, y + 44); c.rotate(((i*37) % 7 - 3)*0.02); c.fillStyle = 'rgba(0,0,0,.25)'; c.fillRect(-52, -40, 108, 88); c.fillStyle = SO_COLS[num(v.c) | 0] || SO_COLS[0]; c.fillRect(-55, -44, 108, 88);
    c.fillStyle = '#3a2e20'; c.font = '15px sans-serif'; c.textAlign = 'left'; const words = [...soShow(v.x, 60)]; let line = '', ly = -24, lines = 0;
    for(const ch of words){ if(c.measureText(line + ch).width > 96){ c.fillText(line, -48, ly); ly += 18; line = ch; if(++lines >= 3) break; } else line += ch; }
    if(lines < 3 && line) c.fillText(line, -48, ly); c.font = '11px sans-serif'; c.globalAlpha = 0.7; c.fillText(safeNick(v.n), -48, 38); c.restore(); });
  B.tex.needsUpdate = true; }
// 정상에 처음 오르면 방명록 안내 + 게시판 세우기
let soSumT = 0;
function soSummitTick(dt){ const now = performance.now(); if(now - soSumT < 1000) return; soSumT = now;
  if(!SO.fb) return;
  if(!SO_G.board && st.started){ const tp = trail[trail.length-1]; if(Math.hypot(tp.x - st.x, tp.z - st.z) < 160){ soGuestStart(); soBoardMake(); } }
  if(st.inSummit && !SO_G.prompted && st.started){ SO_G.prompted = true; setTimeout(() => { if(!$('soGuest').hidden) return; SO_P.chip = null; soAsk('', '정상 방명록에 한마디 남겨 보세요', '📝 방명록', () => soOpenGuest(), 12); }, 4500); }
  if(!$('soGuest').hidden) soRenderGuest(); }
$('cGuest').onclick = () => soOpenGuest(); $('soGuestEnd').onclick = () => soOpenGuest();
// 시작: 웹(파이어베이스)에서만
FB_READY.then(fb => { if(!fb) return; SO.fb = fb; SO.web = true; try{ soChatStart(fb); }catch(e){ SO.chatOk = false; console.warn(e); } });
window.__so = { SO, SO_P, SO_C, soMembers, soLeader };
'''


def _guest_key(m):
    """같은 정상을 오르는 다른 코스(성판악 → 한라산 백록담)는 방명록을 함께 써요."""
    b = m.get('base')
    if b:
        try:
            bm = json.load(open(os.path.join(HERE, 'mountains', b + '.json')))
            if bm.get('peak', {}).get('ko') == m.get('peak', {}).get('ko'):
                return b
        except Exception:
            pass
    return m['id']


def patch_social(P, m):
    P.rep('</style>', SOCIAL_CSS + '</style>', 1)
    P.rep('<div id="mapWrap"', SOCIAL_HTML + '<div id="mapWrap"', 1)
    # 야영장(정상) 메뉴에 방명록
    P.rep('<button class="btn sec" id="again">', '<button class="btn sec" id="soGuestEnd" type="button">📝 정상 방명록</button>\n    <button class="btn sec" id="again">', 1)
    P.rep('<button id="cFire">', '<button id="cGuest"><span class="e">📝</span>방명록</button>\n    <button id="cFire">', 1)
    # 번역 안 할 곳: 사람이 쓴 글(채팅·포스트잇·이름)
    P.rep("const p = n.parentNode; if(!p || p.nodeName==='SCRIPT' || p.nodeName==='STYLE') return;",
          "const p = n.parentNode; if(!p || p.nodeName==='SCRIPT' || p.nodeName==='STYLE' || (p.closest && p.closest('.ugc'))) return;", 1)
    js = SOCIAL_JS.replace('__GB__', _guest_key(m)).replace('__LC__', 'true' if LOGIN_CHAT else 'false').replace('__LG__', 'true' if LOGIN_GUEST else 'false')
    P.rep("window.__game = {", js + "window.__game = {", 1)
    # 위치 신호에 동행·제안·인삿말 싣기
    P.rep("  if(GEV_PRES && ADMIN_SCOPE === 'all') pkt.ev = GEV_PRES;", "  soPkt(pkt);\n  if(GEV_PRES && ADMIN_SCOPE === 'all') pkt.ev = GEV_PRES;", 1)
    P.rep("a.nick = safeNick(pr.n);", "a.nick = safeNick(pr.n); soPeer(p.peer, a, pr);", 1)
    P.rep("a.say=GREETS[Math.max(0, Math.min(GREETS.length-1, num(pr.wi)|0))];", "a.say=soGreetOf(pr);", 1)
    P.rep("function updateRemotes(dt){", "function updateRemotes(dt){ soTick(dt); soSummitTick(dt);", 1)
    # 따라 걷기: 리더 걸음 빠르기·발걸음에 맞추기 (goal.__fs 빠르기, goal.__ph 걸음 위상)
    P.rep("if(st.stamina < 12) speed *= 0.55;", "if(st.stamina < 12) speed *= 0.55;\n    if(st.goal && st.goal.__fs != null) speed = st.goal.__fs;", 1)
    P.rep("const prevPhase = st.phase; st.phase += speed*dt*2.6/Math.sqrt(PACE);",
          "const prevPhase = st.phase; st.phase += speed*dt*2.6/Math.sqrt(PACE);\n    if(st.goal && st.goal.__ph != null){ const dph = Math.atan2(Math.sin(st.goal.__ph - st.phase), Math.cos(st.goal.__ph - st.phase)); st.phase += dph*Math.min(1, dt*1.6); }", 1)
    # 인사 메뉴 끝에 '인삿말 바꾸기'
    P.rep("if(i === greetIdx) b.className = 'sel'; b.onclick = () => { greetIdx = i; m.hidden = true; doWave(); }; m.appendChild(b); });",
          "if(i === greetIdx) b.className = 'sel'; b.onclick = () => { greetIdx = i; m.hidden = true; doWave(); }; m.appendChild(b); });"
          " { const e = document.createElement('button'); e.textContent = '✏️ 인삿말 바꾸기'; e.style.opacity = '.8'; e.onclick = () => soOpenGreet(); m.appendChild(e); }", 1)
    # 지도: 동행은 초록 고리
    P.rep("  for(const a of remotes.values()) dot(a.x, a.z, hexCss(a.outfit.jacket), big?5:10);",
          "  for(const a of remotes.values()) dot(a.x, a.z, hexCss(a.outfit.jacket), big?5:10);\n  soMapRing(mctx, toU, toV, big);", 1)
    # 로그인하면 인삿말도 여러 기기에
    P.rep("if(typeof c.tent === 'number') store.set('tent', c.tent & 0xffffff);",
          "if(typeof c.tent === 'number') store.set('tent', c.tent & 0xffffff); if(Array.isArray(c.greets) && c.greets.length === GREETS.length) store.set('greets', c.greets.map(g => String(g).slice(0, 20))); else if(c.greets === undefined && num(c.pts)) store.set('greets', null);", 1)
    P.rep("tent: me.tent, pts: store.get('profTs', 0),", "tent: me.tent, greets: store.get('greets', null), pts: store.get('profTs', 0),", 1)
