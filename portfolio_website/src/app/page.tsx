import Image from "next/image";

export default function Home() {
  return (
    <main className="min-h-screen p-4 md:p-8 max-w-7xl mx-auto">
      {/* Hero Section */}
      <section className="py-12 md:py-20 text-center md:text-left">
        <div className="max-w-3xl">
          <h1 className="text-4xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary-light to-primary bg-clip-text text-transparent">
            Data Science & AI Laboratory
          </h1>
          <p className="text-lg md:text-xl text-text-light mb-8 leading-relaxed">
            A collection of interactive experiments in Data Engineering, Machine Learning, and Applied Mathematics. 
            Explore real-time data pipelines, predictive models, and physics simulations.
          </p>
          <div className="flex flex-wrap gap-4 justify-center md:justify-start">
            <span className="px-4 py-2 rounded-full bg-surface-soft border border-border text-sm font-medium text-primary-light">
              Cloudflare Workers
            </span>
            <span className="px-4 py-2 rounded-full bg-surface-soft border border-border text-sm font-medium text-primary-light">
              Python & ML
            </span>
            <span className="px-4 py-2 rounded-full bg-surface-soft border border-border text-sm font-medium text-primary-light">
              Next.js & React
            </span>
          </div>
        </div>
      </section>

      {/* Projects Grid */}
      <section className="py-8">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h2 className="text-2xl font-bold text-text-main">Laboratory Collection</h2>
            <p className="text-text-light mt-1">Pick a sandbox to start experimenting</p>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Project Card 1 */}
          <ProjectCard 
            chip="Data Eng · Cloudflare"
            title="Poland Quality Living MVP"
            desc="Serverless ETL pipeline aggregating real-time economic data into Cloudflare D1, serving sub-millisecond queries via Edge Workers."
            href="#"
          />
          {/* Project Card 2 */}
          <ProjectCard 
            chip="Visualization · Vue.js"
            title="Cost Living Chart"
            desc="Interactive data visualization dashboard featuring dynamic filtering and comparative analysis of purchasing power parity across regions."
            href="#"
          />
          {/* Project Card 3 */}
          <ProjectCard 
            chip="Python · Numerical"
            title="Applied Math Library"
            desc="High-performance numerical computing library implementing Newton-Raphson root finding, Romberg integration, and matrix decompositions."
            href="#"
          />
          {/* Project Card 4 */}
          <ProjectCard 
            chip="Python · Physics"
            title="Physics Simulator"
            desc="Deterministic physics engine simulating rigid body dynamics, collision resolution, and conservation laws using Verlet integration."
            href="#"
          />
           {/* Project Card 5 */}
           <ProjectCard 
            chip="ML · Scikit-learn"
            title="ML Model Deployment"
            desc="End-to-end MLOps pipeline deploying Scikit-learn models via API, featuring model versioning, input validation, and drift monitoring."
            href="#"
          />
        </div>
      </section>
    </main>
  );
}

function ProjectCard({ chip, title, desc, href }: { chip: string, title: string, desc: string, href: string }) {
  return (
    <a href={href} className="group block p-6 rounded-2xl bg-card-bg border border-border hover:border-primary/50 transition-all duration-300 hover:shadow-lg hover:-translate-y-1">
      <div className="mb-4">
        <span className="inline-block px-3 py-1 rounded-full text-xs font-semibold bg-primary/10 text-primary-light border border-primary/20">
          {chip}
        </span>
      </div>
      <h3 className="text-xl font-bold mb-3 text-text-main group-hover:text-primary transition-colors">
        {title}
      </h3>
      <p className="text-text-light text-sm leading-relaxed">
        {desc}
      </p>
      <div className="mt-6 flex items-center text-primary text-sm font-medium opacity-0 group-hover:opacity-100 transition-opacity">
        Launch Lab <span className="ml-2">→</span>
      </div>
    </a>
  );
}
