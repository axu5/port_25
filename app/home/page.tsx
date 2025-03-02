import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Input } from "@/components/ui/input";
import { redirect } from "next/navigation";
import { cookies } from "next/headers";
import { ProfileType } from "../ProfileType";
import { Separator } from "@/components/ui/separator";
import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import Link from "next/link";
import { AtSign } from "lucide-react";

export default async function HomePage() {
  const cookieStore = await cookies();
  const cookie = cookieStore.get("profile");
  if (!cookie || !cookie.value) {
    redirect("/");
  }
  const profile = JSON.parse(cookie.value) as ProfileType;
  const initials = profile.name.replace(/[a-z ]+/g, "");

  const similarProfiles = [
    {
      name: "Dr. Samuel Kaski",
      email: "samuel.kaski@aalto.fi",
      scholarLink:
        "https://scholar.google.com/citations?user=example_id",
      organizationalPosition:
        "Professor, Department of Computer Science, Aalto University; Director, Finnish Center for Artificial Intelligence (FCAI)",
      currentInterests: [
        "Probabilistic modeling",
        "Machine learning",
        "Computational biology",
        "Interactive AI",
      ],
      currentWork:
        "I am leading research in probabilistic modeling and interactive AI, focusing on applications in computational biology and personalized medicine. As the director of FCAI, I oversee initiatives that bridge academia and industry to advance AI research and its practical applications.",
    },
    {
      name: "Dr. Erkki Oja",
      email: "erkki.oja@aalto.fi",
      scholarLink:
        "https://scholar.google.com/citations?user=example_id",
      organizationalPosition:
        "Aalto Distinguished Professor Emeritus, Department of Computer Science, Aalto University",
      currentInterests: [
        "Neural networks",
        "Pattern recognition",
        "Machine learning algorithms",
      ],
      currentWork:
        "Although retired, I remain active in the AI research community, focusing on neural networks and pattern recognition. I continue to contribute to the development of machine learning algorithms and mentor young researchers in the field.",
    },
    {
      name: "Dr. Aapo Hyvärinen",
      email: "aapo.hyvärinen@aalto.fi",
      scholarLink:
        "https://scholar.google.com/citations?user=example_id",
      organizationalPosition:
        "Professor, Department of Computer Science, University of Helsinki; Collaborator, Finnish Center for Artificial Intelligence (FCAI)",
      currentInterests: [
        "Unsupervised machine learning",
        "Independent component analysis",
        "Computational neuroscience",
      ],
      currentWork:
        "I am conducting research on unsupervised machine learning methods, particularly independent component analysis, and their applications in computational neuroscience. Through my collaboration with FCAI, I aim to develop AI systems that can learn representations from unstructured data.",
    },
    {
      name: "Mikko Laaksonen",
      email: "mikko.laaksonen@aalto.fi",
      scholarLink:
        "https://scholar.google.com/citations?user=example_id",
      organizationalPosition:
        "Doctoral Researcher, Department of Computer Science, Aalto University",
      currentInterests: [
        "Bayesian methods",
        "Probabilistic programming",
        "Machine learning workflows",
      ],
      currentWork:
        "I am developing robust Bayesian workflows for model selection and diagnostics, aiming to enhance the reliability of probabilistic programming frameworks. My research also involves creating tools to streamline machine learning workflows for data scientists.",
    },
    {
      name: "Liisa Virtanen",
      email: "liisa.virtanen@aalto.fi",
      scholarLink:
        "https://scholar.google.com/citations?user=example_id",
      organizationalPosition:
        "Doctoral Researcher, Finnish Center for Artificial Intelligence (FCAI), Aalto University",
      currentInterests: [
        "Privacy-preserving machine learning",
        "Differential privacy",
        "Secure multi-party computation",
      ],
      currentWork:
        "My research focuses on developing privacy-preserving machine learning algorithms, particularly in the context of healthcare data. I am working on integrating differential privacy techniques with secure multi-party computation to enable collaborative model training without compromising individual privacy.",
    },
    {
      name: "Jussi Korhonen",
      email: "jussi.korhonen@aalto.fi",
      scholarLink:
        "https://scholar.google.com/citations?user=example_id",
      organizationalPosition:
        "Doctoral Researcher, Department of Signal Processing and Acoustics, Aalto University",
      currentInterests: [
        "Reinforcement learning",
        "Robotics",
        "Autonomous systems",
      ],
      currentWork:
        "I am investigating reinforcement learning algorithms for robotic applications, aiming to improve the adaptability and efficiency of autonomous systems. My current project involves developing learning strategies for robots operating in dynamic environments.",
    },
  ];

  return (
    <div className='flex flex-col gap-y-5'>
      <div className='flex flex-row justify-between gap-x-10'>
        <h1 className='font-semibold text-3xl'>Acamatch</h1>
        <Input placeholder='Search' />
        <Avatar>
          <AvatarFallback>{initials}</AvatarFallback>
        </Avatar>
      </div>
      <Separator />
      <div className='grid grid-cols-1 lg:grid-cols-3 gap-5'>
        {similarProfiles.map(profile => (
          <Card key={profile.name} className='flex flex-col'>
            <CardHeader>
              <CardTitle>{profile.name}</CardTitle>
              <CardDescription>
                <Link
                  href={`mailto:${profile.email}`}
                  className='flex flex-row gap-x-1 items-center'>
                  <AtSign className='w-4 h-4' />
                  {profile.email}
                </Link>
              </CardDescription>
              <CardDescription>
                {profile.organizationalPosition}
              </CardDescription>
            </CardHeader>
            <CardContent>{profile.currentWork}</CardContent>
            <CardFooter className='flex flex-col gap-y-3 mt-auto'>
              <Separator />
              <div className='flex flex-wrap gap-1'>
                {profile.currentInterests.map(interest => (
                  <Badge key={interest} variant='outline'>
                    {interest}
                  </Badge>
                ))}
              </div>
            </CardFooter>
          </Card>
        ))}
      </div>
    </div>
  );
}
