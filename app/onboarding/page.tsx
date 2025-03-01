import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResearchInterests from "./ResearchInterests";

export default async function OnboardingPage() {
  async function submit(data: FormData) {
    "use server";
    const name = data.get("name");
    const googleScholar = data.get("name");
    const position = data.get("name");
    const currentInterests = data.getAll("current-interests");
    const currentWork = data.get("name");
    console.log(
      name,
      googleScholar,
      position,
      currentInterests,
      currentWork
    );
  }

  return (
    <div className='flex flex-col gap-y-10'>
      <h1 className='font-semibold text-3xl'>Onboarding</h1>
      <form
        className='flex flex-col gap-y-3 w-xl mx-auto'
        action={submit}>
        <Label htmlFor='name'>Name</Label>
        <Input
          name='name'
          placeholder='What should others call you?'
          required
        />
        <Label htmlFor='google-scholar'>
          Your Google Scholar link
        </Label>
        <Input
          name='google-scholar'
          placeholder='https://scholar.google.com/...'
          type='url'
          required
        />
        <Label htmlFor='position'>Organizational position</Label>
        <Input
          name='position'
          placeholder='What is your organization title?'
          required
        />
        <ResearchInterests />
        <Label htmlFor='current-work'>Current work</Label>
        <Input
          name='current-work'
          placeholder='What are you working on right now?'
          required
        />
        <Button type='submit' className='cursor-pointer'>
          Start connecting!
        </Button>
      </form>
    </div>
  );
}
