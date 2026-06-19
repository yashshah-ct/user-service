export function validateCheckout(order){
  if(!order || !order.email) throw new Error('email required');
  if(!(order.amount > 0)) throw new Error('amount must be positive');
  return true;
}
