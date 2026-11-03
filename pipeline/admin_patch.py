"""관리자 모드를 승연 님 구글 계정에서만 켜지게 (웹). 비밀번호 + 구글 계정(이메일 해시) 둘 다 맞아야 해요.
미리보기(claude 아티팩트, 파이어베이스 없음)는 비공개라 비밀번호만으로 켜져요.
이메일 원문은 코드에 넣지 않고 SHA-256 해시만 둬요. 진짜 보호는 파이어베이스 규칙(auth.token.email)이 해요."""

ADMIN_MAIL_HASH = '66fbf40f2c12a58d89db570b34b34470b40e9b715c720b3d85123fa53f768f56'

OWNER_JS = r"""
const ADMIN_MAIL_HASH = '%s';
// 지금 로그인한 계정이 관리자(승연 님) 구글 계정인지. login=true면 필요할 때 구글 로그인 창을 띄워요
async function adminOwner(login){
  if(window.claude && window.claude.use) return true;
  const fb = await Promise.race([FB_READY, new Promise(r => setTimeout(() => r(null), 8000))]); if(!fb) return false;
  let u = fb.auth.currentUser;
  if((!u || u.isAnonymous) && login){ toast('관리자 구글 계정으로 로그인해 주세요', 2.5); if(!(await googleLogin())) return false; u = fb.auth.currentUser; }
  if(!u || u.isAnonymous || !u.email) return false;
  try{ return (await sha256hex(String(u.email).trim().toLowerCase())) === ADMIN_MAIL_HASH; }catch(e){ return false; }
}
// 계정이 바뀌면(로그아웃·익명 전환·다른 계정) 관리자 모드를 바로 꺼요
async function adminRecheck(){ if(!document.body.classList.contains('admin')) return; if(await adminOwner(false)) return;
  ADMIN_PW = ''; GEV_SEND = null; ADMIN_SCOPE = 'me'; try{ syncScope(); scopeNote(); }catch(e){} setAdmin(false); $('adminLogin').hidden = true; toast('관리자 계정이 아니어서 관리자 모드를 껐어요', 3); }
""" % ADMIN_MAIL_HASH


def patch_admin(P, m):
    P.rep("async function tryAdmin(){", OWNER_JS + "async function tryAdmin(){", 1)
    # 비밀번호가 맞아도 관리자 구글 계정이 아니면 안 켜져요
    P.rep("if(!ok){ $('adErr').textContent = '비밀번호가 맞지 않아요'; return; } $('adPw').value = ''; $('adminLogin').hidden = true; setAdmin(true);",
          "if(!ok){ $('adErr').textContent = '비밀번호가 맞지 않아요'; return; } $('adPw').value = ''; "
          "if(!(await adminOwner(true))){ $('adErr').textContent = '관리자 구글 계정으로 로그인해야 켤 수 있어요'; return; } "
          "$('adminLogin').hidden = true; setAdmin(true);", 1)
    # 새로고침 후 이어 켜기도 관리자 계정일 때만 (창은 띄우지 않음)
    P.rep("try{ if(sessionStorage.getItem('neungseon.admin') === '1') setAdmin(true), $('adminPanel').hidden = true; }catch(e){}",
          "try{ if(sessionStorage.getItem('neungseon.admin') === '1') adminOwner(false).then(ok => { if(ok){ setAdmin(true); $('adminPanel').hidden = true; } else setAdmin(false); }); }catch(e){}", 1)
    # 로그인 계정이 바뀔 때마다 다시 확인
    P.rep("pushPresence(true); } refreshLoginUI(); });", "pushPresence(true); } refreshLoginUI(); adminRecheck(); });", 1)
