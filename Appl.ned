//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
// 
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
// 
// You should have received a copy of the GNU Lesser General Public License
// along with this program.  If not, see http://www.gnu.org/licenses/.
// 

package veins;
import org.car2x.veins.modules.application.ieee80211p.DemoBaseApplLayer;

simple Appl extends DemoBaseApplLayer
{
	parameters:
		//declarations go here
		@class(Appl);

		double T_CheckCamGen = default(0.01s) @unit(s);
		double T_GenCam_DCC = default(0.1s) @unit(s);
}
