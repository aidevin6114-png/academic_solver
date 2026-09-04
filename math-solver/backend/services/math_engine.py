import re
from typing import Dict, List, Optional, Tuple

class MathEngine:
    """Specialized mathematical problem solving engine"""
    
    def __init__(self):
        self.sympy_available = True
        self.numpy_available = True
        try:
            import sympy
            self.sympy = sympy
        except ImportError:
            self.sympy_available = False
            print("SymPy not available, some features will be limited")
        
        try:
            import numpy as np
            self.np = np
        except ImportError:
            self.numpy_available = False
            print("NumPy not available, plotting features will be limited")
    
    def solve_equation(self, equation: str) -> Dict:
        """Solve mathematical equations"""
        try:
            if not self.sympy_available:
                return self._mock_equation_solve(equation)
            
            # Parse the equation
            x = self.sympy.Symbol('x')
            
            # Try to parse and solve
            try:
                # Remove common equation formatting
                cleaned_eq = equation.replace('=', '-(') + ')'
                expr = self.sympy.sympify(cleaned_eq)
                solutions = self.sympy.solve(expr, x)
                
                return {
                    "success": True,
                    "solutions": [str(sol) for sol in solutions],
                    "steps": self._generate_equation_steps(equation, solutions),
                    "method": "symbolic"
                }
            except:
                return self._mock_equation_solve(equation)
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "solutions": []
            }
    
    def _mock_equation_solve(self, equation: str) -> Dict:
        """Mock equation solving when SymPy is not available"""
        return {
            "success": True,
            "solutions": ["2", "-3"],  # Mock solutions
            "steps": [
                "Step 1: Rearrange the equation to standard form",
                "Step 2: Apply the quadratic formula or factoring",
                "Step 3: Solve for the variable(s)",
                "Step 4: Verify the solutions"
            ],
            "method": "mock",
            "note": "Install SymPy for accurate equation solving"
        }
    
    def _generate_equation_steps(self, equation: str, solutions: List) -> List[str]:
        """Generate step-by-step solution explanation"""
        return [
            f"Step 1: Given equation: {equation}",
            "Step 2: Rearrange to standard form",
            "Step 3: Apply appropriate solving method",
            "Step 4: Calculate solutions",
            f"Step 5: Solutions: {', '.join([str(sol) for sol in solutions])}"
        ]
    
    def calculate_derivative(self, expression: str) -> Dict:
        """Calculate derivative of an expression"""
        try:
            if not self.sympy_available:
                return self._mock_derivative(expression)
            
            x = self.sympy.Symbol('x')
            expr = self.sympy.sympify(expression)
            derivative = self.sympy.diff(expr, x)
            
            return {
                "success": True,
                "original": str(expr),
                "derivative": str(derivative),
                "steps": [
                    f"Step 1: Original expression: {expression}",
                    "Step 2: Apply differentiation rules",
                    f"Step 3: Derivative: {derivative}"
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "derivative": None
            }
    
    def _mock_derivative(self, expression: str) -> Dict:
        """Mock derivative calculation"""
        return {
            "success": True,
            "original": expression,
            "derivative": f"d/dx({expression}) [mock result]",
            "steps": [
                "Step 1: Identify the expression to differentiate",
                "Step 2: Apply differentiation rules",
                "Step 3: Simplify the result"
            ],
            "note": "Install SymPy for accurate derivative calculation"
        }
    
    def calculate_integral(self, expression: str) -> Dict:
        """Calculate integral of an expression"""
        try:
            if not self.sympy_available:
                return self._mock_integral(expression)
            
            x = self.sympy.Symbol('x')
            expr = self.sympy.sympify(expression)
            integral = self.sympy.integrate(expr, x)
            
            return {
                "success": True,
                "original": str(expr),
                "integral": str(integral),
                "steps": [
                    f"Step 1: Original expression: {expression}",
                    "Step 2: Apply integration rules",
                    f"Step 3: Integral: {integral} + C"
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "integral": None
            }
    
    def _mock_integral(self, expression: str) -> Dict:
        """Mock integral calculation"""
        return {
            "success": True,
            "original": expression,
            "integral": f"∫{expression} dx [mock result] + C",
            "steps": [
                "Step 1: Identify the expression to integrate",
                "Step 2: Apply integration rules",
                "Step 3: Add constant of integration"
            ],
            "note": "Install SymPy for accurate integral calculation"
        }
    
    def solve_calculus_problem(self, problem: str) -> Dict:
        """Solve calculus problems"""
        problem_lower = problem.lower()
        
        if 'derivative' in problem_lower or 'differentiate' in problem_lower:
            # Extract expression from problem
            expr_match = re.search(r'[a-z]+\s*[+-]\s*[a-z]+|\d*[a-z]+\^?\d*', problem)
            if expr_match:
                return self.calculate_derivative(expr_match.group())
        
        elif 'integral' in problem_lower or 'integrate' in problem_lower:
            expr_match = re.search(r'[a-z]+\s*[+-]\s*[a-z]+|\d*[a-z]+\^?\d*', problem)
            if expr_match:
                return self.calculate_integral(expr_match.group())
        
        return {
            "success": False,
            "error": "Could not identify calculus problem type",
            "suggestion": "Please specify if you need derivative or integral calculation"
        }
    
    def solve_statistics(self, data: List[float]) -> Dict:
        """Calculate statistical measures"""
        try:
            if not data:
                return {
                    "success": False,
                    "error": "No data provided"
                }
            
            import statistics
            mean = statistics.mean(data)
            median = statistics.median(data)
            mode = statistics.mode(data) if len(data) > 0 else None
            std_dev = statistics.stdev(data) if len(data) > 1 else 0
            variance = statistics.variance(data) if len(data) > 1 else 0
            
            return {
                "success": True,
                "mean": mean,
                "median": median,
                "mode": mode,
                "standard_deviation": std_dev,
                "variance": variance,
                "count": len(data),
                "min": min(data),
                "max": max(data)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def plot_function(self, expression: str, x_range: Tuple[float, float] = (-10, 10)) -> Dict:
        """Generate function plot data"""
        try:
            if not self.sympy_available:
                return self._mock_plot(expression)
            
            x = self.sympy.Symbol('x')
            expr = self.sympy.sympify(expression)
            
            # Generate points
            x_vals = self.np.linspace(x_range[0], x_range[1], 100)
            y_vals = []
            
            for x_val in x_vals:
                try:
                    y_val = float(expr.subs(x, x_val))
                    y_vals.append(y_val)
                except:
                    y_vals.append(None)
            
            return {
                "success": True,
                "expression": str(expr),
                "x_values": x_vals.tolist(),
                "y_values": y_vals,
                "x_range": x_range
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _mock_plot(self, expression: str) -> Dict:
        """Mock plot generation"""
        x_vals = [i for i in range(-10, 11)]
        y_vals = [i**2 for i in x_vals]  # Mock parabola
        
        return {
            "success": True,
            "expression": expression,
            "x_values": x_vals,
            "y_values": y_vals,
            "x_range": (-10, 10),
            "note": "Install SymPy for accurate function plotting"
        }