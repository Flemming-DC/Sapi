
pub fn zip_longest<T, U, It1, It2>(iter1: It1, iter2: It2) 
    -> impl Iterator<Item = (Option<T>, Option<U>)>
    where T: Clone, U: Clone, It1: Iterator<Item = T>, It2: Iterator<Item = U>,
{
    let iter1 = iter1.map(Some).chain(std::iter::repeat(None));
    let iter2 = iter2.map(Some).chain(std::iter::repeat(None));
    iter1.zip(iter2).take_while(|(x, y)| x.is_some() || y.is_some())
}
