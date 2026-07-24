use automerge::{AutoCommit, transaction::Transactable, ReadDoc};
use wasm_bindgen::prelude::*;

#[wasm_bindgen]
pub struct ActorState {
    doc: AutoCommit,
}

#[wasm_bindgen]
impl ActorState {
    #[wasm_bindgen(constructor)]
    pub fn new() -> ActorState {
        let doc = AutoCommit::new();
        ActorState { doc }
    }

    #[wasm_bindgen]
    pub fn mutate_intent(&mut self, intent_key: &str, intent_value: &str) {
        // Create a root map if it doesn't exist, and insert the intent
        let (_, root_id) = self.doc.get(automerge::ROOT, "intents").unwrap().unwrap_or_else(|| {
            let id = self.doc.put_object(automerge::ROOT, "intents", automerge::ObjType::Map).unwrap();
            (automerge::Value::Object(automerge::ObjType::Map), id)
        });
        
        self.doc.put(&root_id, intent_key, intent_value).unwrap();
    }

    #[wasm_bindgen]
    pub fn save(&mut self) -> Vec<u8> {
        self.doc.save()
    }
    
    #[wasm_bindgen]
    pub fn load(data: &[u8]) -> ActorState {
        let doc = AutoCommit::load(data).unwrap();
        ActorState { doc }
    }
}
