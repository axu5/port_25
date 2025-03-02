import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import ResearchInterests from "./ResearchInterests";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { ProfileType } from "../ProfileType";

export default async function OnboardingPage() {
  async function submit(data: FormData) {
    "use server";
    const profile = {
      name: data.get("name"),
      scholar_url: data.get("google-scholar"),
      position: data.get("position"),
      currentInterests: data.getAll("current-interests"),
      currentWork: data.get("current-work"),
    };
    const stringifiedProfile = JSON.stringify(profile);

    await fetch("http://0.0.0.0:8000/process-author/", {
      method: "POST",
      body: stringifiedProfile,
    });

    const cookieStore = await cookies();
    cookieStore.set("profile", stringifiedProfile);

    redirect("/home");
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
