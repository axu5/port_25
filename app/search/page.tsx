export default async function Search({
  searchParams,
}: {
  searchParams: any;
}) {
  console.log(await searchParams);
  return <>hi</>;
}
