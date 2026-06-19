import {validateCheckout} from './validate';
test('rejects empty email', ()=>{ expect(()=>validateCheckout({amount:5})).toThrow(); });
test('rejects negative amount', ()=>{ expect(()=>validateCheckout({email:'a@b.c',amount:-1})).toThrow(); });
