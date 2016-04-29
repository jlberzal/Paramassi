

FSinicial = (self.Coh.data*1*Lr + (Peso1*math.cos(Alpha) - Peso1/9.81*self.AcSis.data*math.sin(Alpha)) * math.tan(math.radians(self.Roz.data))\
		+ (Peso2*math.cos(math.radians(self.b.data)) - Peso2/9.81 * self.AcSis.data * math.sin(math.radians(self.b.data)) * math.tan(math.radians(self.Roz.data))))))
		#((Peso1*math.sin(Alpha) + Peso1/9.81*self.AcSis.data*math.cos(Alpha)) + (Peso2*math.sin(math.radians(self.b.data))+Peso2/9.81*self.AcSis.data*math.cos(math.radians(self.b.data)))))))
			
		