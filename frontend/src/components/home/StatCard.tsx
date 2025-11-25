interface StatCardProps {
  percentage: string;
  description: string;
}

const StatCard = ({ percentage, description }: StatCardProps) => {
  return (
    <div className="bg-card rounded-xl p-6 border border-border shadow-md hover:shadow-lg transition-all">
      <p className="text-4xl font-bold text-primary mb-3">{percentage}</p>
      <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
    </div>
  );
};

export default StatCard;
