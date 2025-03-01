import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Home() {
  return (
    <div className='w-full max-h-screen flex flex-row items-center justify-center gap-x-3 overflow-hidden'>
      <Button variant='outline' asChild>
        <Link href='/onboarding'>Get started</Link>
      </Button>
      <Button variant='secondary' asChild>
        <Link href='/login'>Log in</Link>
      </Button>
    </div>
  );
}
