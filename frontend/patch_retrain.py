import re

with open('src/app/page.tsx', 'r') as f:
    content = f.read()

# 1. Add state for retrainProgress
if "const [retrainProgress, setRetrainProgress] = useState(0);" not in content:
    content = content.replace(
        "const [retrainResult, setRetrainResult] = useState<any>(null);",
        "const [retrainResult, setRetrainResult] = useState<any>(null);\n  const [retrainProgress, setRetrainProgress] = useState(0);"
    )

# 2. Modify handleRetrain
old_handle = """const handleRetrain = async () => {
    try {
      const result = await retrainModel();
      setRetrainResult(result);
      mutateModelStatus(result, false);
    } catch (err) {
      console.error('Retrain trigger failed:', err);
      setRetrainResult({ status: 'error', message: 'Failed to trigger training' });
    }
  };"""

new_handle = """const handleRetrain = async () => {
    try {
      setRetrainResult({ status: 'training_started', message: 'Training in progress...' });
      setRetrainProgress(0);
      
      const interval = setInterval(() => {
        setRetrainProgress(p => {
          if (p >= 95) return 95;
          return p + (95 - p) * 0.15;
        });
      }, 500);

      const result = await retrainModel();
      clearInterval(interval);
      setRetrainProgress(100);
      
      setTimeout(() => {
        setRetrainResult(result);
        mutateModelStatus(result, false);
      }, 600);
    } catch (err) {
      console.error('Retrain trigger failed:', err);
      setRetrainResult({ status: 'error', message: 'Failed to trigger training' });
    }
  };"""

if old_handle in content:
    content = content.replace(old_handle, new_handle)

# 3. Add progress bar UI
old_ui = """<button
            onClick={handleRetrain}
            disabled={isTraining}
            className="flex items-center gap-3 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white rounded-xl px-6 py-3 font-medium transition-all shadow-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} />
            {isTraining ? 'Training in progress...' : 'Initiate Retrain'}
          </button>"""

new_ui = """<div className="flex flex-col gap-4">
            <button
              onClick={handleRetrain}
              disabled={isTraining}
              className="flex items-center justify-center sm:justify-start gap-3 bg-slate-900 hover:bg-slate-800 disabled:bg-slate-300 text-white rounded-xl px-6 py-3 font-medium transition-all shadow-sm w-fit"
            >
              <RefreshCw className={`w-4 h-4 ${isTraining ? 'animate-spin' : ''}`} />
              {isTraining ? 'Training in progress...' : 'Initiate Retrain'}
            </button>
            
            {isTraining && (
              <div className="w-full max-w-sm mt-2">
                <div className="flex justify-between text-xs font-semibold text-slate-500 mb-2">
                  <span>Recompiling weights & running SHAP...</span>
                  <span>{Math.round(retrainProgress)}%</span>
                </div>
                <div className="h-2 w-full bg-slate-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-slate-900 rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${retrainProgress}%` }}
                  />
                </div>
              </div>
            )}
          </div>"""

content = content.replace(old_ui, new_ui)

with open('src/app/page.tsx', 'w') as f:
    f.write(content)
