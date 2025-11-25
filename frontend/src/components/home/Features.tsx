import { Sparkles, Brain, Clock, Target } from "lucide-react";
import { Card } from "@/components/ui/card";

const Features = () => {
  const features = [
    {
      icon: Brain,
      title: "Інтелектуальний аналіз",
      description: "AI аналізує ваші задачі та пропонує оптимальний розклад дня з урахуванням пріоритетів та енергії"
    },
    {
      icon: Clock,
      title: "Адаптивне планування",
      description: "Система автоматично перерозподіляє задачі при змінах у вашому графіку"
    },
    {
      icon: Target,
      title: "Фокус на результат",
      description: "Допомагає зосередитися на найважливіших задачах та досягати цілей швидше"
    },
    {
      icon: Sparkles,
      title: "Прості рекомендації",
      description: "Отримуйте персоналізовані поради для підвищення продуктивності"
    }
  ];

  return (
    <section id="features" className="py-20 px-6">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            Можливості Flowly
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Інтелектуальний помічник, який допомагає керувати часом ефективніше
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <Card 
                key={index}
                className="p-8 bg-card/50 backdrop-blur-sm border-border/50 hover:border-primary/50 transition-all duration-300 hover:shadow-lg"
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-lg bg-primary/10">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-xl font-semibold mb-2 text-foreground">
                      {feature.title}
                    </h3>
                    <p className="text-muted-foreground leading-relaxed">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default Features;
