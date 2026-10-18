'use strict';
// Public client key. Database RLS controls all writes; no admin secret is used.
const HomeStore=(()=>{
 const db=window.supabase.createClient('https://uoclpzlkzeaqyzmledon.supabase.co','sb_publishable__GAT4yvgHT17pKQik7pIpg_05zelW_p');
 return {
  async read(){const out={};for(let start=0;;start+=1000){const {data,error}=await db.from('home_decisions').select('listing_key,decision,updated_at').order('listing_key').range(start,start+999);if(error)throw error;for(const row of data)out[row.listing_key]=row;if(data.length<1000)return out;}},
  async member(){const {data:{session},error}=await db.auth.getSession();if(error)throw error;if(!session)return {user:null,allowed:false};const {data,error:e}=await db.from('home_members').select('user_id').eq('user_id',session.user.id);if(e)throw e;return {user:session.user,allowed:data.length===1};},
  async save(listing_key,decision){const {data:{user},error}=await db.auth.getUser();if(error||!user)throw error||Error('Sign in required');const result=await db.from('home_decisions').upsert({listing_key,decision,updated_by:user.id},{onConflict:'listing_key'}).select('listing_key,decision,updated_at').single();if(result.error)throw result.error;return result.data;},
  async signIn(email,password){const {error}=await db.auth.signInWithPassword({email,password});if(error)throw error;},
  async signOut(){const {error}=await db.auth.signOut();if(error)throw error;}
 };
})();
