import Header from "@/components/layout/Header";
import Hero from "@/components/home/Hero";
import Features from "@/components/home/Features";
import HowItWorks from "@/components/home/HowItWorks";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[hsl(320,100%,95%)] to-[hsl(250,100%,95%)]">
      <Header />
      <Hero />
      <Features />
      <HowItWorks />
    </div>
  );
};

export default Index;
